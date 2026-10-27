#!/usr/bin/env python3
"""Local SDD-evo runner. Same-user evidence, NOT a sandbox or attestation."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
import uuid


class Blocked(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise Blocked(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def filehash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, 'DUPLICATE_JSON_KEY')
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(Blocked('INVALID_JSON')))


def save(path, value):
    tmp = path.with_suffix('.tmp')
    require(not tmp.is_symlink() and not path.is_symlink(), 'UNSAFE_STATE')
    with tmp.open('w') as f:
        os.chmod(tmp, 0o600)
        json.dump(value, f, indent=2)
        f.write('\n')
    tmp.replace(path)


def safe(root, name, directory=False):
    require(isinstance(name, str) and name and '\\' not in name and
            not name.startswith('/') and all(x not in ('', '.', '..') for x in name.split('/')),
            'UNSAFE_PATH')
    require(name.split('/')[0] not in ('.git', '.sdd'), 'RESERVED_PATH')
    path = root
    for part in name.split('/'):
        path = path / part
        require(not path.is_symlink(), 'SYMLINK_INPUT')
    require(path.is_dir() if directory else path.is_file(), 'MISSING_INPUT')
    return path


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)


def snapshot(root):
    names = set(git(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0')) - {b''}
    files = {}
    for raw in sorted(names):
        name = os.fsdecode(raw)
        if name == '.sdd' or name.startswith('.sdd/'):
            continue
        path = root / name
        # Never follow symlink parents; hash leaf link text, not its target.
        require(not any(p.is_symlink() for p in path.parents if p != root and root in p.parents), 'SYMLINK_PARENT')
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            files[name] = ['deleted']
            continue
        if stat.S_ISLNK(mode):
            files[name] = ['link', os.readlink(path)]
        else:
            require(stat.S_ISREG(mode), 'UNSUPPORTED_SOURCE_TYPE')
            files[name] = ['file', bool(mode & 0o111), filehash(path)]
    return digest({'head': git(root, 'rev-parse', 'HEAD').decode().strip(),
                   'tree': git(root, 'rev-parse', 'HEAD^{tree}').decode().strip(),
                   'index': hashlib.sha256(git(root, 'ls-files', '--stage', '-z')).hexdigest(),
                   'files': files})


def validate(root, contract, config):
    require(contract.get('schema') == 1 and config.get('schema') == 1, 'INVALID_SCHEMA')
    for key in ('id', 'outcome', 'accepted_basis'):
        require(isinstance(contract.get(key), str) and contract[key].strip(), 'INVALID_CONTRACT')
    reqs = contract.get('requirements')
    require(isinstance(reqs, dict) and reqs and all(re.fullmatch(r'R[0-9]+', k) and isinstance(v, str) and v.strip() for k, v in reqs.items()), 'INVALID_REQUIREMENTS')
    require(isinstance(contract.get('non_goals'), list) and all(isinstance(x, str) for x in contract['non_goals']), 'INVALID_NON_GOALS')
    require(contract.get('manual_review') is True, 'MANUAL_REVIEW_REQUIRED')
    checks = config.get('checks')
    require(isinstance(checks, dict) and checks and all(re.fullmatch(r'[a-z][a-z0-9_-]*', k) for k in checks), 'NO_CHECKS')
    require(isinstance(contract.get('checks'), list) and set(contract['checks']) == set(checks) and len(contract['checks']) == len(checks), 'CHECK_SET_MISMATCH')
    require(type(config.get('max_runs')) is int and 1 <= config['max_runs'] <= 100, 'INVALID_BUDGET')
    require(type(config.get('output_limit')) is int and 1024 <= config['output_limit'] <= 1048576, 'INVALID_OUTPUT_LIMIT')
    env = config.get('env')
    require(isinstance(env, dict) and all(isinstance(k, str) and isinstance(v, str) and '=' not in k and '\0' not in k + v for k, v in env.items()), 'INVALID_ENV')
    for check in checks.values():
        require(check.get('adapter') == 'unittest', 'UNKNOWN_ADAPTER')
        argv = check.get('argv')
        require(isinstance(argv, list) and argv and all(isinstance(x, str) and x and '\0' not in x for x in argv), 'INVALID_ARGV')
        require(Path(argv[0]).is_absolute() and Path(argv[0]).is_file(), 'ABSOLUTE_EXECUTABLE_REQUIRED')
        require(type(check.get('timeout')) in (int, float) and 0 < check['timeout'] <= 3600, 'INVALID_TIMEOUT')
        require(type(check.get('min_tests')) is int and check['min_tests'] > 0, 'INVALID_MIN_TESTS')
        if check.get('cwd') != '.':
            safe(root, check.get('cwd'), directory=True)
    protected = config.get('protected_files')
    require(isinstance(protected, list) and protected, 'PROTECTED_TEST_FILES_REQUIRED')
    for name in protected + contract.get('spec_files', []):
        safe(root, name)


def inputs(root, state):
    contract = load(safe(root, state['contract']))
    config = load(safe(root, state['config']))
    validate(root, contract, config)
    pins = {'contract': digest(contract), 'config': digest(config),
            'protected': {p: filehash(safe(root, p)) for p in config['protected_files']},
            'specs': {p: filehash(safe(root, p)) for p in contract.get('spec_files', [])}}
    return contract, config, pins


def identity(root, pins, config):
    return digest({'source': snapshot(root), 'pins': pins,
                   'runner': filehash(Path(__file__).resolve()),
                   'python': sys.version, 'platform': sys.platform,
                   'executables': {v['argv'][0]: filehash(Path(v['argv'][0])) for v in config['checks'].values()},
                   'environment': config['env']})


def run_check(root, check, config, log):
    started = time.monotonic()
    data = {'stdout': bytearray(), 'stderr': bytearray()}
    outcome = 'pass'
    proc = subprocess.Popen(check['argv'], cwd=root / check['cwd'], env=config['env'],
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True, shell=False)
    assert proc.stdout is not None and proc.stderr is not None
    sel = selectors.DefaultSelector()
    for key, pipe in [('stdout', proc.stdout), ('stderr', proc.stderr)]:
        os.set_blocking(pipe.fileno(), False)
        sel.register(pipe, selectors.EVENT_READ, key)
    try:
        while sel.get_map() or proc.poll() is None:
            if time.monotonic() - started > check['timeout']:
                outcome = 'timeout'
                break
            for key, _ in sel.select(0.05):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                room = config['output_limit'] - len(data[key.data])
                data[key.data].extend(chunk[:max(0, room)])
                if len(chunk) > room:
                    outcome = 'output_limit'
                    break
            if outcome != 'pass':
                break
    finally:
        # Also terminate descendants holding pipes after their parent exits.
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        sel.close()
        proc.stdout.close()
        proc.stderr.close()
    text = bytes(data['stdout'] + data['stderr']).decode('utf-8', errors='replace')
    counts = re.findall(r'^Ran (\d+) tests? in ', text, re.M)
    if outcome == 'pass' and (proc.returncode != 0 or len(counts) != 1 or int(counts[0]) < check['min_tests'] or
                              not re.search(r'^OK\s*$', text, re.M) or re.search(r'skipped=|expected failures=|unexpected successes=', text)):
        outcome = 'fail'
    artifacts = {}
    for key, content in data.items():
        path = log / (key + '.txt')
        path.write_bytes(content)
        os.chmod(path, 0o600)
        artifacts[key] = filehash(path)
    return {'status': outcome, 'exit_code': proc.returncode, 'tests': int(counts[0]) if len(counts) == 1 else 0,
            'artifacts': artifacts}


def assess(root, state, config, pins):
    require(state['pins'] == pins, 'AMENDMENT_REQUIRED')
    receipt = load(root / '.sdd' / 'receipt.json')
    current = identity(root, pins, config)
    require(receipt.get('identity') == current and receipt.get('terminal_identity') == current, 'STALE_EVIDENCE')
    require(receipt.get('run') == state['runs'], 'LOST_OR_OLD_RECEIPT')
    results = receipt.get('results')
    require(isinstance(results, dict) and set(results) == set(config['checks']), 'CHECK_SET_MISMATCH')
    require(re.fullmatch(r'[0-9a-f]{32}', receipt.get('token', '')) is not None, 'INVALID_RECEIPT')
    for name, result in results.items():
        require(result.get('status') == 'pass' and type(result.get('exit_code')) is int and result['exit_code'] == 0 and
                type(result.get('tests')) is int and result['tests'] >= config['checks'][name]['min_tests'], 'CHECK_NOT_PASS')
        require(set(result.get('artifacts', {})) == {'stdout', 'stderr'}, 'LOST_ARTIFACT')
        for stream, expected in result['artifacts'].items():
            path = root / '.sdd' / receipt['token'] / name / (stream + '.txt')
            require(path.is_file() and filehash(path) == expected, 'LOST_ARTIFACT')
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('init')
    p = sub.add_parser('start')
    p.add_argument('--contract', default='evo-contract.json')
    p.add_argument('--config', default='evo-config.json')
    p.add_argument('--accept', required=True, help='local accepting person/reference; not authentication')
    sub.add_parser('status')
    sub.add_parser('check')
    p = sub.add_parser('change')
    p.add_argument('--accept', required=True)
    p.add_argument('--reason', required=True)
    p = sub.add_parser('review')
    p.add_argument('--by', required=True)
    p.add_argument('--evidence', required=True, help='repo-relative review note file')
    sub.add_parser('finish')
    args = parser.parse_args()
    try:
        root = Path(args.repo).resolve()
        require(Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() == root, 'REPO_ROOT_REQUIRED')
        os.umask(0o077)
        sd = root / '.sdd'
        require(not sd.is_symlink(), 'UNSAFE_STATE')
        sd.mkdir(exist_ok=True)
        require(not any(p.is_symlink() for p in sd.rglob('*')), 'UNSAFE_STATE')
        # .sdd must be ignored before any local records/logs are created.
        require(subprocess.run(['git', '-C', str(root), 'check-ignore', '-q', '.sdd/probe']).returncode == 0 and
                not git(root, 'ls-files', '.sdd'), 'IGNORE_SDD_FIRST')
        with (sd / 'lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return dispatch(root, sd, args)
    except (Blocked, OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as exc:
        reason = str(exc) if isinstance(exc, Blocked) else 'INVALID_OR_MISSING_INPUT'
        print(json.dumps({'state': 'BLOCKED', 'reason': reason, 'released': False,
                          'next': 'Inspect inputs/status; repair code or explicitly accept an amendment. Do not weaken acceptance.'}))
        return 3


def dispatch(root, sd, args):
    action = args.action
    if action == 'init':
        require(not (root / 'evo-contract.json').exists() and not (root / 'evo-config.json').exists(), 'INPUTS_EXIST')
        save(root / 'evo-contract.json', {'schema': 1, 'id': 'CHANGE-1', 'outcome': 'REPLACE with desired observable outcome',
             'accepted_basis': 'REPLACE with user request/reference', 'requirements': {'R1': 'REPLACE with acceptance criterion'},
             'non_goals': ['No deployment'], 'checks': ['unit'], 'manual_review': True, 'spec_files': []})
        save(root / 'evo-config.json', {'schema': 1, 'max_runs': 5, 'output_limit': 65536,
             'env': {'PATH': os.defpath, 'PYTHONDONTWRITEBYTECODE': '1', 'LC_ALL': 'C.UTF-8'},
             'protected_files': ['test_app.py'], 'checks': {'unit': {'adapter': 'unittest',
             'argv': [sys.executable, '-m', 'unittest', '-v', 'test_app'], 'cwd': '.', 'timeout': 30, 'min_tests': 1}}})
        print(json.dumps({'state': 'DRAFT', 'next': 'Edit both evo JSON files; inspect trusted argv/tests, then start --accept NAME.', 'released': False}))
        return 0
    if action == 'start':
        require(not (sd / 'state.json').exists(), 'ALREADY_STARTED')
        require(args.accept.strip(), 'ACCEPTANCE_REQUIRED')
        state = {'contract': args.contract, 'config': args.config, 'runs': 0, 'history': []}
        contract, config, pins = inputs(root, state)
        require('REPLACE' not in json.dumps(contract), 'EDIT_CONTRACT_FIRST')
        state.update(pins=pins, budget=config['max_runs'], accepted_by=args.accept)
        state['history'].append({'kind': 'start', 'pins': pins, 'accepted_by': args.accept})
        save(sd / 'state.json', state)
        print(json.dumps({'state': 'READY', 'next': 'Implement the contract; run check. No model is invoked.', 'released': False}))
        return 0
    state = load(sd / 'state.json')
    contract, config, pins = inputs(root, state)
    if action == 'change':
        require(args.accept.strip() and args.reason.strip(), 'EXPLICIT_AMENDMENT_REQUIRED')
        require(state['pins'] != pins, 'NO_AMENDMENT_CHANGE')
        require(config['max_runs'] == state['budget'], 'BUDGET_CANNOT_RESET')
        state['history'].append({'kind': 'amendment', 'before': state['pins'], 'after': pins,
                                 'accepted_by': args.accept, 'reason': args.reason})
        state['pins'] = pins
        save(sd / 'state.json', state)
        for name in ('receipt.json', 'review.json', 'finish.json'):
            (sd / name).unlink(missing_ok=True)
        print(json.dumps({'state': 'READY', 'next': 'Amendment recorded locally; rebuild and check. Runs are not reset.', 'released': False}))
        return 0
    require(state['pins'] == pins, 'AMENDMENT_REQUIRED')
    if action == 'check':
        require(type(state['runs']) is int and 0 <= state['runs'] < state['budget'], 'BUDGET_EXHAUSTED')
        before = identity(root, pins, config)
        state['runs'] += 1
        save(sd / 'state.json', state)
        for name in ('receipt.json', 'review.json', 'finish.json'):
            (sd / name).unlink(missing_ok=True)
        token = uuid.uuid4().hex
        results = {}
        for name, check in config['checks'].items():
            log = sd / token / name
            log.mkdir(parents=True)
            results[name] = run_check(root, check, config, log)
        _, end_config, end_pins = inputs(root, state)
        receipt = {'identity': before, 'terminal_identity': identity(root, end_pins, end_config),
                   'run': state['runs'], 'token': token, 'results': results}
        save(sd / 'receipt.json', receipt)
        assess(root, state, config, pins)
        print(json.dumps({'state': 'VERIFIED', 'manual_review': 'PENDING', 'run': state['runs'], 'released': False,
                          'next': 'Perform human/domain/UX review, write evidence note, check again if source changed, then review.'}))
        return 0
    current = assess(root, state, config, pins)
    if action == 'review':
        require(args.by.strip(), 'REVIEWER_REQUIRED')
        note = safe(root, args.evidence)
        require(note.stat().st_size > 0, 'EMPTY_REVIEW')
        save(sd / 'review.json', {'identity': current, 'by': args.by, 'evidence': args.evidence, 'hash': filehash(note)})
    review_ok = False
    if (sd / 'review.json').exists():
        review = load(sd / 'review.json')
        review_ok = (review.get('identity') == current and bool(review.get('by')) and
                     filehash(safe(root, review['evidence'])) == review.get('hash'))
    if action == 'finish':
        require(review_ok, 'MANUAL_REVIEW_REQUIRED')
        save(sd / 'finish.json', {'identity': current, 'state': 'ACCEPTED_LOCAL', 'released': False})
    print(json.dumps({'state': 'ACCEPTED_LOCAL' if action == 'finish' else 'VERIFIED',
                      'manual_review': 'RECORDED_LOCAL' if review_ok else 'PENDING', 'released': False,
                      'runs_used': state['runs'], 'max_runs': state['budget'],
                      'next': 'Local acceptance only; release/merge require separate authority and checks.' if action == 'finish' else 'Record review then finish; changed inputs require fresh checks.'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
