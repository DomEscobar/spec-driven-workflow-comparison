"""GitHub API protocol TEST DOUBLE only: never contacts GitHub."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_pipeline as base

spec = importlib.util.spec_from_file_location('publisher', Path(__file__).with_name('publish.py'))
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class GitHubProtocol(unittest.TestCase):
    setUp = base.Pipeline.setUp
    tearDown = base.Pipeline.tearDown
    git = base.Pipeline.git
    setup_job = base.Pipeline.setup_job
    envelope = base.Pipeline.envelope

    def ready(self):
        self.git('remote', 'add', 'origin', 'https://github.com/example/fixture.git')
        j = self.setup_job(adapter='external', publish_repo='example/fixture', publish_base='main', publisher_home=str(self.root))
        self.c.drive(j)
        self.c.import_result(j, self.envelope(j, edits={'calc.py': 'def add(a,b):\n    return a+b\n'}))
        self.c.drive(j)
        self.c.import_result(j, self.envelope(j, verdict='accept', findings=[]))
        return j

    def transport(self, j):
        state = {'refs': {}, 'prs': [], 'creates': 0}
        def fake(job, argv, cwd, child_env, label, container=None):
            self.assertEqual(cwd, self.c.root)
            self.assertNotIn('HERMES_HOME', child_env)
            path = argv[2].removeprefix('repos/example/fixture/')
            data = json.loads(Path(argv[-1]).read_text()) if '--input' in argv else None
            if path == '': result = {'full_name': 'example/fixture', 'private': True}
            elif path == 'git/ref/heads/main': result = {'object': {'sha': j['base']}}
            elif path == 'git/commits/' + j['base']: result = {'tree': {'sha': 'baseline-tree'}}
            elif path == 'git/trees':
                entries = []
                for e in data['tree']:
                    raw = e['content'].encode()
                    sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                    entries.append(dict(path=e['path'], mode=e['mode'], sha=sha))
                result = {'sha': 'test-tree', 'tree': entries}
            elif path == 'git/commits':
                state['commit'] = dict(sha='test-commit', tree={'sha': data['tree']}, parents=[{'sha': x} for x in data['parents']], message=data['message'])
                result = state['commit']
            elif path == 'git/commits/test-commit': result = state['commit']
            elif path.startswith('git/ref/heads/sdd-evo/'):
                if 'branch' not in state:
                    return 1, json.dumps({'message': 'Not Found', 'status': '404'})
                result = {'object': {'sha': state['branch']}}
            elif path == 'git/refs':
                state['branch'] = data['sha']; result = {'object': {'sha': state['branch']}}
            elif path.startswith('pulls?'): result = state['prs']
            elif path == 'pulls':
                state['creates'] += 1
                pr = {'number': 1, 'html_url': 'https://github.com/example/fixture/pull/1', 'body': data['body'], 'state': 'open', 'draft': True, 'maintainer_can_modify': False,
                      'head': {'sha': state['branch'], 'ref': data['head'], 'repo': {'full_name': 'example/fixture'}},
                      'base': {'ref': data['base'], 'sha': j['base'], 'repo': {'full_name': 'example/fixture'}}}
                state['prs'] = [pr]; result = pr
            elif path == 'pulls/1': result = state['prs'][0]
            else: self.fail('Unexpected protocol path: ' + path)
            return 0, json.dumps(result)
        return state, fake

    def test_explicit_authority_required_before_network(self):
        j = self.ready()
        with patch.object(self.c, 'execute') as execute:
            with self.assertRaisesRegex(ValueError, 'EXPLICIT_PUBLISH_PR'): publisher.publish(self.c, j, False)
            execute.assert_not_called()

    def test_exact_readback_and_duplicate_reconciliation(self):
        j = self.ready(); state, fake = self.transport(j)
        with patch.object(self.c, 'execute', side_effect=fake):
            publisher.publish(self.c, j, True)
            self.assertEqual(j['state'], 'published')
            publisher.publish(self.c, j, True)
            self.assertEqual(state['creates'], 1)
            self.assertEqual(j['pr_number'], 1)

    def test_remote_branch_conflict_not_overwritten(self):
        j = self.ready(); state, fake = self.transport(j)
        state['branch'] = 'unrelated'
        with patch.object(self.c, 'execute', side_effect=fake):
            with self.assertRaisesRegex(ValueError, 'REMOTE_BRANCH_CONFLICT'): publisher.publish(self.c, j, True)
        self.assertEqual(state['creates'], 0)

    def test_pr_body_tamper_rejected(self):
        j = self.ready(); state, fake = self.transport(j)
        with patch.object(self.c, 'execute', side_effect=fake):
            publisher.publish(self.c, j, True)
            state['prs'][0]['body'] = 'changed elsewhere'
            with self.assertRaisesRegex(ValueError, 'PR_READBACK_MISMATCH'): publisher.publish(self.c, j, True)
        self.assertEqual(state['creates'], 1)


if __name__ == '__main__': unittest.main(verbosity=2)
