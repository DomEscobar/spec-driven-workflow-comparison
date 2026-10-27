"""Real CLI subprocesses and real temporary Git repositories; no PASS fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'evo.py'


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put('.gitignore', '.sdd/\n__pycache__/\n')
        self.put('app.py', 'def add(a, b): return a + b\n')
        self.put('test_app.py', 'import unittest\nfrom app import add\nclass Test(unittest.TestCase):\n def test_add(self): self.assertEqual(add(2, 3), 5)\n')
        self.put('review.md', 'R1 inspected: addition works; no UI required. Local human review example.\n')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@invalid', 'commit', '-qm', 'base')
        self.cli('init')
        c = self.read('evo-contract.json')
        c.update(outcome='Add two numbers', accepted_basis='Explicit fixture task', requirements={'R1': '2 + 3 = 5'})
        self.json('evo-contract.json', c)
        self.cli('start', '--accept', 'fixture-owner')

    def put(self, name, text):
        (self.root / name).write_text(text)

    def read(self, name):
        return json.loads((self.root / name).read_text())

    def json(self, name, value):
        self.put(name, json.dumps(value))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT)

    def cli(self, *args, code=0):
        p = subprocess.run([sys.executable, str(CLI), '--repo', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(p.returncode, code, p.stdout + p.stderr)
        return json.loads(p.stdout)

    def finish(self):
        self.cli('review', '--by', 'fixture-reviewer', '--evidence', 'review.md')
        self.assertEqual(self.cli('finish')['state'], 'ACCEPTED_LOCAL')

    def amend(self):
        self.cli('change', '--accept', 'fixture-owner', '--reason', 'Explicit test scenario amendment')

    def test_real_bug_fix_finish_and_stale(self):
        self.put('app.py', 'def add(a, b): return a - b\n')
        self.assertEqual(self.cli('check', code=3)['reason'], 'CHECK_NOT_PASS')
        self.put('app.py', 'def add(a, b): return a + b\n')
        self.cli('check')
        self.finish()
        self.put('app.py', 'def add(a, b): return 0\n')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'STALE_EVIDENCE')

    def test_repeat_no_self_hash(self):
        self.cli('check')
        self.cli('check')
        self.finish()
        self.cli('status')

    def test_untracked_source_invalidates(self):
        self.cli('check')
        self.put('new.py', '# untracked\n')
        self.cli('finish', code=3)

    def test_tracked_deletion_invalidates(self):
        self.cli('check')
        (self.root / 'app.py').unlink()
        self.cli('finish', code=3)

    def test_dirty_index_invalidates(self):
        self.cli('check')
        self.git('add', 'evo-contract.json')
        self.cli('finish', code=3)

    def test_test_edit_requires_amendment(self):
        self.cli('check')
        with (self.root / 'test_app.py').open('a') as f:
            f.write('# changed test\n')
        self.assertEqual(self.cli('check', code=3)['reason'], 'AMENDMENT_REQUIRED')
        self.amend()
        self.cli('finish', code=3)
        self.cli('check')
        self.finish()

    def test_contract_change_invalidates(self):
        self.cli('check')
        c = self.read('evo-contract.json')
        c['requirements']['R2'] = 'Document addition'
        self.json('evo-contract.json', c)
        self.cli('finish', code=3)
        self.amend()
        self.cli('finish', code=3)

    def test_config_environment_invalidates(self):
        self.cli('check')
        c = self.read('evo-config.json')
        c['env']['DECLARED_VERSION'] = 'changed'
        self.json('evo-config.json', c)
        self.cli('finish', code=3)

    def test_timeout(self):
        c = self.read('evo-config.json')
        c['checks']['unit']['argv'] = [sys.executable, '-c', 'import time; time.sleep(3)']
        c['checks']['unit']['timeout'] = 0.1
        self.json('evo-config.json', c)
        self.amend()
        self.cli('check', code=3)
        self.assertEqual(self.read('.sdd/receipt.json')['results']['unit']['status'], 'timeout')

    def test_output_bound(self):
        c = self.read('evo-config.json')
        c['checks']['unit']['argv'] = [sys.executable, '-c', 'print("x" * 100000)']
        c['output_limit'] = 1024
        self.json('evo-config.json', c)
        self.amend()
        self.cli('check', code=3)
        r = self.read('.sdd/receipt.json')
        self.assertEqual(r['results']['unit']['status'], 'output_limit')
        self.assertLessEqual((self.root / '.sdd' / r['token'] / 'unit/stdout.txt').stat().st_size, 1024)

    def test_lost_receipt(self):
        self.cli('check')
        (self.root / '.sdd/receipt.json').unlink()
        self.cli('finish', code=3)

    def test_lost_log(self):
        self.cli('check')
        r = self.read('.sdd/receipt.json')
        (self.root / '.sdd' / r['token'] / 'unit/stdout.txt').unlink()
        self.cli('finish', code=3)

    def test_unknown_results(self):
        self.cli('check')
        r = self.read('.sdd/receipt.json')
        r['results']['unit']['status'] = 'unknown'
        self.json('.sdd/receipt.json', r)
        self.cli('finish', code=3)

    def test_no_checks(self):
        c = self.read('evo-config.json')
        c['checks'] = {}
        self.json('evo-config.json', c)
        self.cli('check', code=3)

    def test_zero_tests_and_skipped_fail(self):
        for text in ['import unittest\n', 'import unittest\nclass Test(unittest.TestCase):\n @unittest.skip("not done")\n def test_skip(self): pass\n']:
            self.put('test_app.py', text)
            self.amend()
            self.cli('check', code=3)

    def test_malicious_paths(self):
        for path in ['../outside', '/tmp/outside', '.sdd/receipt.json', 'a/../app.py', 'a\\b']:
            c = self.read('evo-contract.json')
            c['spec_files'] = [path]
            self.json('evo-contract.json', c)
            self.cli('change', '--accept', 'owner', '--reason', 'test', code=3)

    def test_external_specs_hashed(self):
        self.put('spec.md', 'Accepted external spec')
        c = self.read('evo-contract.json')
        c['spec_files'] = ['spec.md']
        self.json('evo-contract.json', c)
        self.amend()
        self.cli('check')
        self.put('spec.md', 'Changed')
        self.cli('finish', code=3)

    def test_symlink_not_followed(self):
        (self.root / 'link').symlink_to('/not/a/real/path')
        self.cli('check')
        (self.root / 'link').unlink()
        (self.root / 'link').symlink_to('/other/path')
        self.cli('finish', code=3)

    def test_state_symlink_rejected(self):
        (self.root / '.sdd/evil').symlink_to(self.root / 'app.py')
        self.cli('check', code=3)

    def test_missing_review_blocks(self):
        self.cli('check')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'MANUAL_REVIEW_REQUIRED')

    def test_budget_cumulative(self):
        for _ in range(5):
            self.cli('check')
        self.assertEqual(self.cli('check', code=3)['reason'], 'BUDGET_EXHAUSTED')

    def test_run_does_not_touch_git_or_other_repo(self):
        before = self.git('status', '--porcelain')
        self.cli('check')
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_config_command_invalidates(self):
        self.cli('check')
        c = self.read('evo-config.json')
        c['checks']['unit']['argv'].append('test_app')
        self.json('evo-config.json', c)
        self.assertEqual(self.cli('finish', code=3)['reason'], 'AMENDMENT_REQUIRED')

    def test_missing_result(self):
        self.cli('check')
        r = self.read('.sdd/receipt.json')
        r['results'] = {}
        self.json('.sdd/receipt.json', r)
        self.assertEqual(self.cli('finish', code=3)['reason'], 'CHECK_SET_MISMATCH')

    def test_review_note_change_invalidates(self):
        self.cli('check')
        self.finish()
        self.put('review.md', 'different review')
        self.cli('finish', code=3)

    def test_protected_symlink_rejected(self):
        (self.root / 'test_app.py').unlink()
        (self.root / 'test_app.py').symlink_to(self.root / 'app.py')
        self.cli('check', code=3)

    def test_budget_amendment_cannot_reset(self):
        self.cli('check')
        c = self.read('evo-config.json')
        c['max_runs'] = 20
        self.json('evo-config.json', c)
        self.assertEqual(self.cli('change', '--accept', 'owner', '--reason', 'increase', code=3)['reason'], 'BUDGET_CANNOT_RESET')
        self.assertEqual(self.read('.sdd/state.json')['runs'], 1)

    def test_ignored_tracked_file_is_still_bound(self):
        self.put('tracked.cache', 'v1')
        self.git('add', 'tracked.cache')
        self.put('.gitignore', '.sdd/\n__pycache__/\n*.cache\n')
        self.cli('check')
        self.put('tracked.cache', 'v2')
        self.cli('finish', code=3)

    def test_ambient_environment_is_not_inherited(self):
        self.put('test_app.py', 'import os,unittest\nclass Test(unittest.TestCase):\n def test_env(self): self.assertNotIn("EVO_TEST_PRIVATE", os.environ)\n')
        self.amend()
        old = os.environ.get('EVO_TEST_PRIVATE')
        os.environ['EVO_TEST_PRIVATE'] = 'non-secret-test-sentinel'
        try:
            self.cli('check')
        finally:
            if old is None:
                del os.environ['EVO_TEST_PRIVATE']
            else:
                os.environ['EVO_TEST_PRIVATE'] = old

    def test_changed_during_run(self):
        c = self.read('evo-config.json')
        c['checks']['unit']['argv'] = [sys.executable, '-c', 'import pathlib,unittest; pathlib.Path("new.txt").write_text("mutation"); unittest.main(module="test_app", verbosity=2)']
        self.json('evo-config.json', c)
        self.amend()
        self.assertEqual(self.cli('check', code=3)['reason'], 'STALE_EVIDENCE')


if __name__ == '__main__':
    unittest.main()
