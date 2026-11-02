"""Real Git + subprocess tests; agents/critic are explicitly deterministic fixtures."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('controller', HERE / 'controller.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Deterministic fixture')
        (self.repo / 'calc.py').write_text('def add(a, b):\n    return 0\n')
        (self.repo / 'test_calc.py').write_text('import unittest\nfrom calc import add\nclass Addition(unittest.TestCase):\n    def test_add(self): self.assertEqual(add(2, 3), 5)\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture baseline')
        self.c = m.Controller(self.root / 'state')
        self.cfg = dict(repo=str(self.repo), profile='fixture-profile', project='fixture-project',
                        trusted_repo=True, adapter='fixture', fixture_only=True,
                        worker=str(HERE / 'fixture_worker.py'), risk='low', execution='trusted-local',
                        allowed_files=['calc.py'], protected_files=['test_calc.py'],
                        checks=[{'argv': [sys.executable, '-m', 'unittest', 'discover', '-v'], 'min_tests': 1}])

    def tearDown(self):
        self.c.db.close()
        self.tmp.cleanup()

    def git(self, *args):
        return m.git(self.repo, *args)

    def setup_job(self, **changes):
        self.cfg.update(changes)
        self.c.configure(self.cfg)
        return self.c.start('Implement addition for two numbers.', 'task-1')

    def envelope(self, j, **fields):
        r = j['request']
        return dict({k: r[k] for k in ('schema', 'job', 'role', 'nonce', 'source')}, **fields)

    def test_full_real_git_checks_fixture_agents(self):
        j = self.setup_job()
        with self.c.lock(): self.c.drive(j)
        self.assertEqual(j['state'], 'pr-ready')
        self.assertEqual((j['runs'], j['repairs'], j['reviews']), (2, 1, 1))
        self.assertEqual(j['acceptance'], 'machine-policy')
        self.assertIn('FAILED', (self.c.root / j['id'] / 'check-1-0.log').read_text())
        self.assertIn('OK', (self.c.root / j['id'] / 'check-2-0.log').read_text())
        self.assertIn('+    return a + b', (self.c.root / j['id'] / 'candidate.diff').read_text())
        self.assertIn('return 0', (self.repo / 'calc.py').read_text())
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertEqual(m.git(self.c.workspace(j), 'remote'), '')

    def test_duplicate_jobs_and_key_conflict(self):
        j = self.setup_job()
        self.assertEqual(self.c.start(j['requirement'], 'task-1')['id'], j['id'])
        with self.assertRaisesRegex(m.evo.Blocked, 'IDEMPOTENCY_CONFLICT'):
            self.c.start('different requirement', 'task-1')

    def test_external_restart_and_fresh_critic(self):
        j = self.setup_job(adapter='external')
        self.c.drive(j)
        nonce = j['request']['nonce']
        self.c.db.close()
        self.c = m.Controller(self.root / 'state')
        j = self.c.job(j['id'])
        self.c.drive(j)
        self.assertEqual(nonce, j['request']['nonce'])
        self.c.import_result(j, self.envelope(j, edits={'calc.py': 'def add(a,b):\n    return a+b\n'}))
        self.c.drive(j)
        self.assertEqual(j['state'], 'waiting-critic')
        self.assertNotEqual(nonce, j['request']['nonce'])
        self.c.import_result(j, self.envelope(j, verdict='accept', findings=[]))
        self.assertEqual(j['state'], 'pr-ready')

    def test_stale_result(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        result = self.envelope(j, edits={})
        (self.c.workspace(j) / 'calc.py').write_text('changed')
        with self.assertRaisesRegex(m.evo.Blocked, 'STALE_RESULT'): self.c.import_result(j, result)

    def test_protected_change(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        (self.c.workspace(j) / 'test_calc.py').write_text('pass')
        with self.assertRaisesRegex(m.evo.Blocked, 'PROTECTED_CHANGED'): self.c.guard(j)

    def test_edit_scope_preflight_no_partial_write(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        for path in ('../escape', '/tmp/escape', 'test_calc.py', '.git/config'):
            result = self.envelope(j, edits={'calc.py': 'bad', path: 'bad'})
            with self.assertRaisesRegex(m.evo.Blocked, 'EDIT_SCOPE'): self.c.import_result(j, result)
            self.assertIn('return 0', (self.c.workspace(j) / 'calc.py').read_text())
        self.assertFalse((self.c.root / j['id'] / 'escape').exists())

    def test_artifact_tamper(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        (self.c.root / j['id'] / 'request.json').write_text('{}')
        with self.assertRaisesRegex(m.evo.Blocked, 'ARTIFACT_TAMPER'): self.c.guard(j)

    def test_stale_verified(self):
        j = self.setup_job(); self.c.drive(j)
        (self.c.workspace(j) / 'calc.py').write_text('wrong')
        with self.assertRaisesRegex(m.evo.Blocked, 'STALE_EVIDENCE'): self.c.guard(j)

    def test_run_budget(self):
        j = self.setup_job(max_runs=1)
        with self.assertRaisesRegex(m.evo.Blocked, 'RUN_LIMIT'): self.c.drive(j)
        self.assertEqual(j['runs'], 1)

    def test_review_budget(self):
        j = self.setup_job(adapter='external', max_reviews=1); self.c.drive(j)
        self.c.import_result(j, self.envelope(j, edits={'calc.py': 'def add(a,b):\n    return a+b\n'})); self.c.drive(j)
        self.c.import_result(j, self.envelope(j, verdict='repair', findings=['Need a clearer implementation.']))
        self.c.drive(j)
        self.c.import_result(j, self.envelope(j, edits={}))
        with self.assertRaisesRegex(m.evo.Blocked, 'REVIEW_LIMIT'): self.c.drive(j)

    def test_human_policy_never_impersonated(self):
        j = self.setup_job(risk='human'); self.c.drive(j)
        self.assertEqual(j['state'], 'needs-human')
        self.assertNotIn('human-approved', json.dumps(j))

    def test_crash_ambiguous_never_rerun(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        j['inflight'] = {'label': 'worker', 'pid': 99999999}; self.c.save(j)
        j = self.c.job(j['id']); self.c.drive(j)
        self.assertEqual(j['state'], 'reconcile-required')
        self.assertEqual(j['calls'], 1)

    def test_cancel_preserves_nonprocess_effect_intent(self):
        j = self.setup_job(adapter='external')
        for state in ('cloning', 'applying', 'publishing', 'reconcile-required'):
            with self.subTest(state=state):
                j['state'] = state; self.c.save(j)
                self.c.cancel(j['id'])
                fresh = self.c.job(j['id'])
                self.assertEqual(fresh['state'], 'reconcile-required')

    def test_apply_io_failure_preserves_reconciliation_barrier(self):
        from unittest.mock import patch
        j = self.setup_job(adapter='external'); self.c.drive(j)
        write = Path.write_text
        target = self.c.workspace(j) / 'calc.py'
        def partial_write(path, text, *args, **kwargs):
            if path == target:
                write(path, 'partial')
                raise OSError('injected write failure')
            return write(path, text, *args, **kwargs)
        with patch.object(Path, 'write_text', partial_write):
            try:
                self.c.import_result(j, self.envelope(j, edits={'calc.py': 'def add(a,b): return a+b\n'}))
            except OSError as exc:
                self.c.fail(j, exc)
        self.assertEqual(target.read_text(), 'partial')
        self.assertEqual(self.c.job(j['id'])['state'], 'reconcile-required')

    def test_lock_exclusion(self):
        self.setup_job()
        other = m.Controller(self.c.root)
        try:
            with self.c.lock():
                with self.assertRaisesRegex(m.evo.Blocked, 'CONTROLLER_BUSY'):
                    with other.lock(): pass
        finally: other.db.close()

    def test_config_pin(self):
        j = self.setup_job()
        c = json.loads((self.c.root / 'config.json').read_text()); c['risk'] = 'human'
        (self.c.root / 'config.json').write_text(json.dumps(c))
        with self.assertRaisesRegex(m.evo.Blocked, 'CONFIG_TAMPER'): self.c.job(j['id'])

    def test_walltime(self):
        j = self.setup_job(walltime=1); j['created'] -= 2
        with self.assertRaisesRegex(m.evo.Blocked, 'WALLTIME_LIMIT'): self.c.drive(j)

    def test_output_cap_and_redaction(self):
        j = self.setup_job()
        with self.assertRaisesRegex(m.evo.Blocked, 'OUTPUT_LIMIT'):
            self.c.execute(j, [sys.executable, '-c', 'print("X"*300000)'], self.root, m.env('/tmp'), 'large')
        self.assertLessEqual((self.c.root / j['id'] / 'large.log').stat().st_size, m.LIMIT)
        self.assertEqual(m.redact('token=abcdefghijk'), '[REDACTED]')

    def test_timeout(self):
        j = self.setup_job(timeout=1)
        with self.assertRaisesRegex(m.evo.Blocked, 'PROCESS_TIMEOUT'):
            self.c.execute(j, [sys.executable, '-c', 'import time;time.sleep(30)'], self.root, m.env('/tmp'), 'timeout')

    def test_cancel_running_process_group(self):
        j = self.setup_job()
        def cancel():
            time.sleep(.2)
            c = m.Controller(self.c.root)
            c.cancel(j['id']); c.db.close()
        t = threading.Thread(target=cancel); t.start()
        try:
            with self.assertRaisesRegex(m.evo.Blocked, 'cancelled'):
                self.c.execute(j, [sys.executable, '-c', 'import subprocess,time;p=subprocess.Popen(["sleep","30"]);print(p.pid,flush=True);time.sleep(30)'], self.root, m.env('/tmp'), 'cancel')
        finally: t.join()
        self.assertNotIn('inflight', j)
        child = int((self.c.root / j['id'] / 'cancel.log').read_text().strip())
        path = Path(f'/proc/{child}/stat')
        deadline = time.monotonic() + 3
        while path.exists() and path.read_text().rsplit(')', 1)[1].split()[0] != 'Z' and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(not path.exists() or path.read_text().rsplit(')', 1)[1].split()[0] == 'Z')

    def test_environment_no_parent_credentials(self):
        j = self.setup_job()
        os.environ['SDD_TEST_SECRET'] = 'do-not-inherit'
        try:
            code, text = self.c.execute(j, [sys.executable, '-c', 'import os;print("SDD_TEST_SECRET" in os.environ)'], self.root, m.env('/tmp'), 'env')
            self.assertEqual((code, text.strip()), (0, 'False'))
        finally: os.environ.pop('SDD_TEST_SECRET')

    def test_symlink_rejected(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        p = self.c.workspace(j) / 'calc.py'; p.unlink(); p.symlink_to(self.repo / 'calc.py')
        with self.assertRaisesRegex(m.evo.Blocked, 'SYMLINK'): self.c.guard(j)

    def test_cli_status_resume(self):
        j = self.setup_job(adapter='external')
        for command in ('run', 'status', 'resume'):
            p = subprocess.run([sys.executable, str(HERE / 'controller.py'), '--state', str(self.c.root), command, j['id']], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
            self.assertEqual(json.loads(p.stdout)['state'], 'waiting-builder')

    def test_actual_controller_crash_resume_and_orphan_cancel(self):
        worker = self.root / 'slow.py'
        worker.write_text('import time;time.sleep(30)')
        j = self.setup_job(worker=str(worker))
        proc = subprocess.Popen([sys.executable, str(HERE / 'controller.py'), '--state', str(self.c.root), 'run', j['id']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid = None
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                live = self.c.job(j['id']).get('inflight', {})
                if live.get('label', '').startswith('worker-') and live.get('pid'):
                    pid = live['pid']; break
                time.sleep(.02)
            self.assertIsNotNone(pid)
            proc.kill(); proc.communicate(timeout=3)
            j = self.c.job(j['id']); self.c.drive(j)
            self.assertEqual(j['state'], 'reconcile-required')
            self.assertEqual(j['calls'], 1)
            self.c.cancel(j['id'])
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                path = Path(f'/proc/{pid}/stat')
                if not path.exists() or path.read_text().rsplit(')', 1)[1].split()[0] == 'Z': break
                time.sleep(.02)
            else: self.fail('orphan remained alive')
        finally:
            if proc.poll() is None: proc.kill(); proc.communicate()
            if pid:
                try: os.killpg(pid, signal.SIGKILL)
                except ProcessLookupError: pass

    def test_completed_side_effect_crash_does_not_replay(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        j['completed_effect'] = {'label': 'worker', 'exit': 0}; self.c.save(j)
        self.c.drive(j)
        self.assertEqual(j['state'], 'reconcile-required')

    def test_unsupported_provider_and_unapproved_spend(self):
        self.cfg['adapter'] = 'codex'
        with self.assertRaisesRegex(m.evo.Blocked, 'UNSUPPORTED_ADAPTER'): self.c.configure(self.cfg)
        self.cfg.update(adapter='hermes', hermes_binary=sys.executable, provider='example', model='example')
        with self.assertRaisesRegex(m.evo.Blocked, 'EXPLICIT_SPEND'): self.c.configure(self.cfg)

    def test_unresolved_finding_not_implicitly_erased(self):
        j = self.setup_job(adapter='external'); self.c.drive(j)
        self.c.import_result(j, self.envelope(j, edits={'calc.py': 'def add(a,b):\n    return a+b\n'})); self.c.drive(j)
        self.c.import_result(j, self.envelope(j, verdict='repair', findings=['R1 concern']))
        self.c.drive(j); self.c.import_result(j, self.envelope(j, edits={})); self.c.drive(j)
        with self.assertRaisesRegex(m.evo.Blocked, 'UNDISPOSED_FINDINGS'):
            self.c.import_result(j, self.envelope(j, verdict='accept', findings=[]))
        self.c.import_result(j, self.envelope(j, verdict='accept', findings=[], addressed=['R1 concern']))
        self.assertEqual(j['state'], 'pr-ready')

    def test_hermes_cli_mapping_with_mocked_inference_only(self):
        from unittest.mock import patch
        home = self.c.root / 'provider' / 'test'
        home.mkdir(parents=True)
        j = self.setup_job(adapter='hermes', hermes_binary=sys.executable,
                           hermes_home=str(home), provider='test-only', model='test-only',
                           spend_approval='UNIT TEST mock transport, no inference authorized', max_calls=3)
        execute = self.c.execute
        seen = []
        def mocked(job, argv, cwd, child_env, label, container=None):
            if not label.startswith('worker-'):
                return execute(job, argv, cwd, child_env, label, container)
            seen.append(argv)
            self.assertIn('--safe-mode', argv)
            self.assertNotIn('--resume', argv)
            self.assertEqual(argv[-2:], ['-t', 'clarify'])
            self.assertEqual(child_env['HERMES_HOME'], str(home))
            self.assertNotIn('GH_TOKEN', child_env)
            r = job['request']
            if r['role'] == 'builder':
                result = self.envelope(job, edits={'calc.py': 'def add(a,b):\n    return a+b\n'})
            else: result = self.envelope(job, verdict='accept', findings=[])
            return 0, 'session metadata\n<sdd-result>' + json.dumps(result) + '</sdd-result>\nSession: test-only'
        with patch.object(self.c, 'execute', side_effect=mocked): self.c.drive(j)
        self.assertEqual(j['state'], 'pr-ready')
        self.assertEqual(j['provider_calls'], 2)
        self.assertEqual(len(seen), 2)

    def test_repair_cap_and_pending_cancel(self):
        j = self.setup_job(adapter='external', max_repairs=1)
        self.c.repair(j)
        with self.assertRaisesRegex(m.evo.Blocked, 'REPAIR_LIMIT'): self.c.repair(j)
        self.c.cancel(j['id'])
        self.assertEqual(self.c.job(j['id'])['state'], 'cancelled')

    @unittest.skipUnless(os.environ.get('SDD_TEST_IMAGE'), 'set SDD_TEST_IMAGE to a local pinned image; no pulls')
    def test_docker_full_flow(self):
        isolation = '''import os, socket, unittest
class Isolation(unittest.TestCase):
    def test_mount_and_credentials(self):
        self.assertEqual(os.getuid(), 65534)
        self.assertIsNone(os.environ.get('GH_TOKEN'))
        self.assertIsNone(os.environ.get('OPENAI_API_KEY'))
        for path in ('/workspace/calc.py', '/host-escape'):
            with self.assertRaises(OSError):
                with open(path, 'w') as f: f.write('escape')
        with self.assertRaises(OSError): socket.create_connection(('1.1.1.1', 443), timeout=0.2)
unittest.main()
'''
        j = self.setup_job(execution='docker', image=os.environ['SDD_TEST_IMAGE'], checks=[
            {'argv': ['/opt/hermes/.venv/bin/python3', '-m', 'unittest', 'discover', '-v'], 'min_tests': 1},
            {'argv': ['/opt/hermes/.venv/bin/python3', '-c', isolation], 'min_tests': 1}])
        self.c.drive(j)
        self.assertEqual(j['state'], 'pr-ready')
        self.assertEqual(j['runs'], 2)


if __name__ == '__main__': unittest.main(verbosity=2)
