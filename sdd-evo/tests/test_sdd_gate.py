import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sdd_gate', ROOT / 'scripts/sdd_gate.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.a, self.c, self.e = [g.load(ROOT / 'fixtures' / (n + '.json'))
                                for n in ('approved', 'current', 'evidence')]

    def check(self, reason=None):
        before = copy.deepcopy((self.a, self.c, self.e))
        answer = g.gate(self.a, self.c, self.e)
        self.assertEqual(before, (self.a, self.c, self.e), 'gate must be pure')
        self.assertFalse(answer['released'])
        if reason:
            self.assertFalse(answer['eligible'])
            self.assertIn(reason, answer['reason_codes'])
        else:
            self.assertTrue(answer['eligible'], answer)
        return answer

    def fresh(self):
        self.e['binding'] = g.binding(self.c)
        self.e['terminal_binding'] = g.binding(self.c)

    def test_valid_not_released(self):
        self.assertEqual(self.check()['state'], 'ACCEPTED')

    def test_stale_spec(self):
        self.c['spec'] += '; amended'
        self.check('UNAUTHORIZED_SPEC')

    def test_authorized_spec_still_requires_fresh_evidence(self):
        self.c['spec'] += '; authorized amendment'
        self.a['pins']['spec'] = g.digest(self.c['spec'])
        self.check('STALE_EVIDENCE')
        self.fresh()
        self.check()

    def test_stale_code(self):
        self.c['candidate']['src/export.py'] += ' changed'
        self.check('STALE_EVIDENCE')

    def test_stale_integration(self):
        self.c['integration']['src/cli.py'] += ' changed'
        self.check('STALE_EVIDENCE')

    def test_stale_developer_tests(self):
        self.c['integration']['tests/dev.py'] = 'new tests'
        self.check('STALE_EVIDENCE')

    def test_oracle_mutation_with_reforged_bindings(self):
        self.c['oracle'] = 'weaker tests'
        self.fresh()
        self.check('UNAUTHORIZED_ORACLE')

    def test_scope_mutation(self):
        self.c['contract']['scope'].append('secrets.txt')
        self.fresh()
        self.check('SCOPE_MUTATION')

    def test_out_of_scope(self):
        self.c['integration']['telemetry.py'] = 'unrequested'
        self.fresh()
        self.check('OUT_OF_SCOPE')

    def test_deletion_out_of_scope(self):
        self.c['base']['protected.txt'] = 'retained'
        self.fresh()
        self.check('OUT_OF_SCOPE')

    def test_task_checkbox_not_evidence(self):
        self.c['tasks'] = [{'done': True}]
        self.e = None
        self.check('EVIDENCE_MISSING')

    def test_identity_mismatch_not_authentication(self):
        self.e['producer'] = 'builder'
        self.check('IDENTITY_MISMATCH')

    def test_unknown_fail_skip_error(self):
        for value in ('unknown', 'skip', 'error', 'fail', None):
            with self.subTest(status=value):
                self.e['checks'][0]['status'] = value
                self.check('CHECK_NOT_PASS')

    def test_missing_check(self):
        self.e['checks'].pop()
        self.check('CHECK_SET_MISMATCH')

    def test_duplicate_check(self):
        self.e['checks'].append(copy.deepcopy(self.e['checks'][0]))
        self.check('CHECK_SET_MISMATCH')

    def test_empty_discovery(self):
        self.e['checks'][0]['observations'] = []
        self.check('EMPTY_OR_DUPLICATE_DISCOVERY')

    def test_incomplete_discovery(self):
        self.e['checks'][0]['observations'] = ['public']
        self.check('INCOMPLETE_DISCOVERY')

    def test_required_checks_cannot_be_removed(self):
        self.c['contract']['required_checks'] = ['privacy']
        self.fresh()
        self.check('CHECK_POLICY_MUTATION')

    def test_missing_deliverable(self):
        del self.c['integration']['src/cli.py']
        self.fresh()
        self.check('MISSING_DELIVERABLE')

    def test_all_input_versions_invalidate(self):
        for key in ('environment', 'commands', 'config', 'instructions', 'base', 'policy'):
            with self.subTest(key=key):
                old = copy.deepcopy(self.c[key])
                if isinstance(self.c[key], dict):
                    self.c[key]['changed'] = 'v2'
                else:
                    self.c[key] += ' v2'
                self.check('STALE_EVIDENCE')
                self.c[key] = old

    def test_old_worker_generation(self):
        self.c['generation'] += 1
        self.check('STALE_EVIDENCE')

    def test_unknown_effect(self):
        self.c['effect_outcome'] = 'unknown'
        self.check('EFFECT_RECONCILIATION_REQUIRED')

    def test_invalid_phase(self):
        self.c['phase'] = 'BUILDING'
        self.check('INVALID_STATE')

    def test_blocked_cannot_accept(self):
        self.c['status'] = 'blocked'
        self.check('INVALID_STATE')

    def test_review_missing(self):
        del self.e['reviewer']
        self.check('REVIEW_MISSING')

    def test_terminal_mutation(self):
        self.e['terminal_binding']['config'] = 'changed during verification'
        self.check('TERMINAL_STATE_MISMATCH')

    def test_valid_alternative_with_fresh_evidence(self):
        self.c['candidate']['src/export.py'] = 'alternative: stream allowlist rather than batch'
        self.c['integration']['src/export.py'] = self.c['candidate']['src/export.py']
        self.fresh()
        self.check()

    def test_path_escape(self):
        self.c['integration']['../outside'] = 'x'
        self.check('INVALID_PATH')

    def test_raw_whitespace_change_is_not_normalized(self):
        self.assertNotEqual(g.digest('a\n'), g.digest('a  \r\n'))

    def test_repair_budget_bound(self):
        ledger = {'used': 0, 'last_fingerprint': None}
        for fingerprint in ('first', 'second'):
            reservation = g.reserve_repair(ledger, 2, fingerprint)
            self.assertTrue(reservation['allowed'])
            ledger = reservation['ledger']
        self.assertEqual(g.reserve_repair(ledger, 2, 'third')['reason'], 'BUDGET_EXHAUSTED')

    def test_no_progress_and_unknown_budget(self):
        self.assertEqual(g.reserve_repair({'used': 1, 'last_fingerprint': 'same'}, 2, 'same')['reason'], 'NO_PROGRESS')
        self.assertEqual(g.reserve_repair({'used': None}, 2, 'new')['reason'], 'UNKNOWN_BUDGET')

    def test_duplicate_json_keys_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            path.write_text('{"schema":1,"schema":2}')
            with self.assertRaises(ValueError):
                g.load(path)

    def test_cli_positive_and_negative(self):
        for current, code in [('current.json', 0), ('stale-current.json', 3)]:
            run = subprocess.run([sys.executable, str(ROOT / 'scripts/sdd_gate.py'), '--demo',
                '--approved', str(ROOT / 'fixtures/approved.json'), '--current', str(ROOT / 'fixtures' / current),
                '--evidence', str(ROOT / 'fixtures/evidence.json')], capture_output=True, text=True)
            self.assertEqual(run.returncode, code, run.stderr)
            self.assertEqual(json.loads(run.stdout)['eligible'], code == 0)


if __name__ == '__main__':
    unittest.main()
