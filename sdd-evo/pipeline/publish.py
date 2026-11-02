"""Narrow parent-only GitHub surface. Never invoked by a worker; no live publication tests.
API objects rather than shell git push: credential never enters workspace or worker env.
"""
import hashlib
import json
import os
from pathlib import Path
import re


def publish(c, j, authorized):
    require = c.config  # config pin is checked on every entry
    cfg = require()

    # Use the controller's pinned evo runtime without a second dynamic module import.
    def insist(ok, why):
        if not ok:
            raise ValueError(why)
    insist(authorized, 'EXPLICIT_PUBLISH_PR_REQUIRED')
    repo = cfg.get('publish_repo', '')
    base = cfg.get('publish_base', '')
    insist(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo), 'PUBLISH_REPO_NOT_AUTHORIZED')
    insist(re.fullmatch(r'[A-Za-z0-9_.-]+', base), 'PUBLISH_BASE_REQUIRED')
    insist(j.get('acceptance') == 'machine-policy' and j.get('verified'), 'MACHINE_ACCEPTANCE_REQUIRED')
    insist(cfg['adapter'] != 'fixture', 'FIXTURE_PUBLICATION_FORBIDDEN')
    insist(j['state'] in ('pr-ready', 'publishing', 'reconcile-required', 'published'), 'NOT_PR_READY')
    c.guard(j)
    insist(not c.stop_reason(j), c.stop_reason(j))
    # Narrow allowlist; do not inherit provider keys, SSH agent or arbitrary Git config.
    child_env = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'LANG': 'C.UTF-8',
                 'HOME': cfg['publisher_home'], 'GH_PROMPT_DISABLED': '1', 'GH_HOST': 'github.com'}
    for key in ('GH_TOKEN', 'GITHUB_TOKEN'):
        if key in os.environ:
            child_env[key] = os.environ[key]
    branch = 'sdd-evo/' + j['id']
    body = 'SDD-evo job ' + j['id'] + '\nSource identity: ' + j['verified'] + '\nAcceptance: machine-policy (not human approval).\n'
    title = 'SDD-evo candidate ' + j['id'][:12]
    j['state'] = 'publishing'
    c.save(j)

    def api(path, payload=None, missing=False):
        j['publish_calls'] = j.get('publish_calls', 0) + 1
        insist(j['publish_calls'] <= 60, 'PUBLISH_CALL_LIMIT')
        c.save(j)
        argv = ['/usr/bin/gh', 'api', 'repos/' + repo + '/' + path]
        if payload is not None:
            p = c.artifact(j, 'publish-input.json', payload)
            # Redaction must never silently alter a remote write payload.
            insist(json.loads(p.read_text()) == payload, 'SENSITIVE_PUBLISH_BLOCKED')
            argv += ['--method', 'POST', '--input', str(p)]
        code, output = c.execute(j, argv, c.root, child_env, 'publish-' + str(j['publish_calls']))
        # gh stderr is merged; parse the leading JSON object, ignoring trailing diagnostics.
        try:
            data, _ = json.JSONDecoder().raw_decode(output.lstrip())
        except ValueError:
            raise ValueError('GH_INVALID_RESPONSE')
        if code and missing and isinstance(data, dict) and data.get('status') == '404':
            return None
        insist(code == 0, 'GH_API_FAILED')
        return data

    # Both local remote and authenticated target must match the preapproved project.
    import subprocess
    remote = subprocess.check_output(['git', '-C', cfg['repo'], 'remote', 'get-url', 'origin'], text=True, timeout=10).strip()
    insist(remote in ('https://github.com/' + repo + '.git', 'git@github.com:' + repo + '.git', 'https://github.com/' + repo), 'REMOTE_MISMATCH')
    metadata = api('')
    insist(metadata['full_name'] == repo and metadata['private'] is True, 'PRIVATE_TARGET_REQUIRED')
    current = api('git/ref/heads/' + base)
    insist(current['object']['sha'] == j['base'], 'REMOTE_BASE_MOVED_REVALIDATE')
    baseline = api('git/commits/' + j['base'])
    w = c.workspace(j)
    entries = []
    for name in cfg['allowed_files']:
        content = (w / name).read_text()
        raw = content.encode()
        sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        entries.append({'path': name, 'mode': '100755' if j['baseline'][name][1] else '100644', 'type': 'blob', 'content': content, 'expected': sha})
    tree = api('git/trees', {'base_tree': baseline['tree']['sha'], 'tree': [{k: v for k, v in e.items() if k != 'expected'} for e in entries]})
    remote_entries = {e['path']: e for e in tree['tree']}
    insist(all(remote_entries[e['path']]['sha'] == e['expected'] and remote_entries[e['path']]['mode'] == e['mode'] for e in entries), 'REMOTE_TREE_MISMATCH')
    if not j.get('publish_sha'):
        commit = api('git/commits', {'message': title + '\n\n' + body, 'tree': tree['sha'], 'parents': [j['base']]})
        j['publish_sha'] = commit['sha']
        j['publish_tree'] = tree['sha']
        c.save(j)
    insist(j['publish_tree'] == tree['sha'], 'PUBLISH_TREE_CHANGED')
    commit = api('git/commits/' + j['publish_sha'])
    insist(commit['tree']['sha'] == tree['sha'] and [p['sha'] for p in commit['parents']] == [j['base']] and commit['message'] == title + '\n\n' + body, 'REMOTE_COMMIT_MISMATCH')
    ref = api('git/ref/heads/' + branch, missing=True)
    if ref is None:
        api('git/refs', {'ref': 'refs/heads/' + branch, 'sha': j['publish_sha']})
    ref = api('git/ref/heads/' + branch)
    insist(ref['object']['sha'] == j['publish_sha'], 'REMOTE_BRANCH_CONFLICT')
    prs = api('pulls?state=all&head=' + repo.split('/')[0] + ':' + branch + '&per_page=100')
    insist(isinstance(prs, list) and len(prs) <= 1, 'DUPLICATE_PRS')
    if prs:
        pr = prs[0]
    else:
        pr = api('pulls', {'title': title, 'head': branch, 'base': base, 'body': body, 'draft': True, 'maintainer_can_modify': False})
    pr = api('pulls/' + str(pr['number']))
    insist(pr['head']['sha'] == j['publish_sha'] and pr['head']['ref'] == branch and pr['head']['repo']['full_name'] == repo and pr['base']['ref'] == base and pr['base']['sha'] == j['base'] and pr['base']['repo']['full_name'] == repo and pr['body'] == body and pr['state'] == 'open' and pr['draft'] is True and pr['maintainer_can_modify'] is False, 'PR_READBACK_MISMATCH')
    insist(api('git/ref/heads/' + base)['object']['sha'] == j['base'], 'REMOTE_BASE_MOVED_REVALIDATE')
    c.guard(j)
    j.update(state='published', pr_url=pr['html_url'], pr_number=pr['number'])
    j.pop('completed_effect', None)
    c.artifact(j, 'published.json', {'sha': j['publish_sha'], 'url': pr['html_url'], 'number': pr['number'], 'body': body})
    c.save(j)
    return j
