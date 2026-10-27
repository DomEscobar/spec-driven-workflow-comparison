"""Real Git/CLI/checks; scripted critic protocol fixtures, NOT an LLM review."""
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import test_evo


class CritiqueTests(unittest.TestCase):
    put = test_evo.RunnerTests.put
    read = test_evo.RunnerTests.read
    json = test_evo.RunnerTests.json
    git = test_evo.RunnerTests.git
    cli = test_evo.RunnerTests.cli
    amend = test_evo.RunnerTests.amend

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.put('.gitignore', '.sdd/\n__pycache__/\n')
        self.put('app.py', 'def add(a,b): return a+b\n')
        self.put('test_app.py', 'import unittest\nfrom app import add\nclass Test(unittest.TestCase):\n def test_add(self): self.assertEqual(add(2,3), 5)\n')
        self.put('review.md', 'Scripted manual-review protocol fixture, not human acceptance.\n')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@invalid', 'commit', '-qm', 'base')
        self.cli('init')
        self.put('brief.md', 'Original authorized user brief: add any two integers, including negatives. No deployment.\n')
        c = self.read('evo-contract.json')
        c.update(outcome='Add integers', accepted_basis='Explicit test fixture', requirements={'R1': '2 + 3 = 5'})
        c['task_brief'] = 'brief.md'
        self.json('evo-contract.json', c)
        cfg = self.read('evo-config.json')
        cfg['critique']['enabled'] = True
        if self._testMethodName == 'test_multiple_rounds_keep_all_findings':
            cfg['critique']['max_reviews'] = 2
        self.json('evo-config.json', cfg)
        self.cli('start', '--accept', 'fixture-owner')
        self.put('app.py', 'def add(a, b): return 0 if a < 0 else a + b\n')
        self.cli('check')

    def prepare(self):
        self.cli('critique-prepare')
        p = self.read('.sdd/critique-package-1.json')
        self.assertEqual(base64.b64decode(p['source']['app.py']['base64']), (self.root / 'app.py').read_bytes())
        self.assertEqual(p['original_brief'], (self.root / 'brief.md').read_text())
        self.assertIn('app.py', p['diff'])
        return p

    def result(self, findings=True):
        p = self.read('.sdd/critique-package-1.json')
        observed = subprocess.check_output([sys.executable, '-B', '-c', 'from app import add; print(add(-2,1))'], cwd=self.root, text=True).strip()
        r = {k: p[k] for k in ('package_id', 'subject', 'contract_id', 'prompt_id')}
        r.update(schema=1, fresh_context=True, critic='scripted-test-fixture-not-independent', model='none', findings=[])
        if findings:
            r['findings'] = [{'id': 'F1', 'requirement': 'BRIEF', 'deviation': 'negative integer sum should be -1',
                              'probe': 'add(-2,1)', 'observation': observed, 'support': 'supported',
                              'severity': 'major', 'uncertainty': 'Only one negative input observed'}]
        self.json('.sdd/critic-result.json', r)
        return r

    def imported(self, findings=True):
        self.prepare()
        self.result(findings)
        self.cli('critique-import')

    def disposition(self, status='fixed'):
        d = {'schema': 1, 'subject': self.read('.sdd/receipt.json')['identity'], 'findings': {
            '1/F1': {'status': status, 'rationale': 'Reproduced negative case and repaired addition',
                     'probe': 'add(-2,1)', 'observation': '-1', 'uncertainty': 'Finite checks, no universal proof'}}}
        self.json('.sdd/dispositions.json', d)
        return d

    def test_real_repair_e2e(self):
        self.imported()
        self.assertEqual(self.cli('finish', code=3)['reason'], 'FINDINGS_DISPOSITION_REQUIRED')
        self.put('app.py', 'def add(a, b): return a + b\n')
        self.cli('critique-dispose', '--by', 'test-owner', code=3)
        self.cli('check')
        observed = subprocess.check_output([sys.executable, '-B', '-c', 'from app import add; print(add(-2,1))'], cwd=self.root, text=True).strip()
        self.assertEqual(observed, '-1')
        self.disposition()
        self.cli('critique-dispose', '--by', 'test-owner')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'MANUAL_REVIEW_REQUIRED')
        self.cli('review', '--by', 'scripted-example-not-human', '--evidence', 'review.md')
        self.assertEqual(self.cli('finish')['state'], 'ACCEPTED_LOCAL')
        self.put('app.py', 'def add(a, b): return 99\n')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'STALE_EVIDENCE')
        self.assertEqual(self.cli('check', code=3)['reason'], 'REPAIR_BUDGET_EXHAUSTED')
        c = self.read('.sdd/state.json')['critique']
        self.assertEqual((c['reviews'], c['repairs']), (1, 1))

    def test_stale_import(self):
        self.prepare()
        self.result()
        self.put('app.py', 'def add(a,b): return a+b\n')
        self.assertEqual(self.cli('critique-import', code=3)['reason'], 'STALE_EVIDENCE')
        self.assertEqual(self.cli('check', code=3)['reason'], 'IMPORT_BEFORE_REPAIR')

    def test_required_review_and_dispositions_even_empty(self):
        self.assertEqual(self.cli('finish', code=3)['reason'], 'CRITIQUE_REQUIRED')
        self.imported(False)
        self.cli('review', '--by', 'owner', '--evidence', 'review.md', code=3)
        self.json('.sdd/dispositions.json', {'schema': 1, 'subject': self.read('.sdd/receipt.json')['identity'], 'findings': {}})
        self.cli('critique-dispose', '--by', 'owner')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'MANUAL_REVIEW_REQUIRED')

    def test_missing_invalid_and_unresolved_findings(self):
        self.imported()
        d = self.disposition('refuted')
        for rows, reason in [({}, 'MISSING_FINDING_RESOLUTIONS'),
                             ({'1/F1': {'status': 'refuted'}}, 'INVALID_DISPOSITION_EVIDENCE')]:
            d['findings'] = rows
            self.json('.sdd/dispositions.json', d)
            self.assertEqual(self.cli('critique-dispose', '--by', 'owner', code=3)['reason'], reason)
        for status in ('open', 'accepted_risk'):
            self.disposition(status)
            self.assertEqual(self.cli('critique-dispose', '--by', 'owner', code=3)['reason'], 'UNRESOLVED_FINDING')
        self.disposition('fixed')
        self.assertEqual(self.cli('critique-dispose', '--by', 'owner', code=3)['reason'], 'REPAIR_CHECK_REQUIRED')

    def test_malformed_result_and_identity(self):
        self.prepare()
        r = self.result()
        for key, value in [('subject', 'wrong'), ('findings', [{}]), ('fresh_context', False), ('model', '')]:
            bad = dict(r)
            bad[key] = value
            self.json('.sdd/critic-result.json', bad)
            self.cli('critique-import', code=3)
        self.put('.sdd/critic-result.json', '{broken')
        self.cli('critique-import', code=3)
        self.json('.sdd/critic-result.json', r)
        self.cli('critique-import')
        self.cli('critique-import', code=3)

    def test_lost_and_modified_receipts(self):
        self.imported()
        path = self.root / '.sdd/critique-result-1.json'
        original = path.read_text()
        path.write_text('{}')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'LOST_CRITIQUE_ARTIFACT')
        path.write_text(original)
        path.unlink()
        self.cli('finish', code=3)

    def test_review_and_repair_budgets_distinct(self):
        self.imported()
        self.assertEqual(self.cli('critique-prepare', code=3)['reason'], 'REVIEW_BUDGET_EXHAUSTED')
        self.cli('check')  # same subject does not spend a repair
        self.assertEqual(self.read('.sdd/state.json')['critique']['repairs'], 0)
        self.put('app.py', 'def add(a,b): return 99\n')
        self.assertEqual(self.cli('check', code=3)['reason'], 'CHECK_NOT_PASS')
        self.assertEqual(self.read('.sdd/state.json')['critique']['repairs'], 1)
        self.put('app.py', 'def add(a,b): return a+b\n')
        self.assertEqual(self.cli('check', code=3)['reason'], 'REPAIR_BUDGET_EXHAUSTED')

    def test_toggle_cannot_bypass_and_limits_cannot_reset(self):
        self.imported()
        cfg = self.read('evo-config.json')
        cfg['critique']['enabled'] = False
        self.json('evo-config.json', cfg)
        self.assertEqual(self.cli('finish', code=3)['reason'], 'AMENDMENT_REQUIRED')
        self.assertEqual(self.cli('change', '--accept', 'owner', '--reason', 'disable', code=3)['reason'], 'CRITIQUE_ACTIVE_AMENDMENT_BLOCKED')

    def test_authorized_toggle_before_prepare(self):
        cfg = self.read('evo-config.json')
        cfg['critique']['enabled'] = False
        self.json('evo-config.json', cfg)
        self.cli('check', code=3)
        self.amend()
        self.cli('check')
        self.cli('critique-prepare', code=3)
        self.assertEqual(self.cli('finish', code=3)['reason'], 'MANUAL_REVIEW_REQUIRED')
        cfg['critique']['max_reviews'] = 2
        self.json('evo-config.json', cfg)
        self.assertEqual(self.cli('change', '--accept', 'owner', '--reason', 'increase', code=3)['reason'], 'CRITIQUE_BUDGET_CANNOT_RESET')

    def test_brief_is_protected(self):
        self.put('brief.md', 'Changed authorization')
        self.assertEqual(self.cli('critique-prepare', code=3)['reason'], 'AMENDMENT_REQUIRED')

    def test_multiple_rounds_keep_all_findings(self):
        self.imported()
        self.cli('critique-prepare')
        p = self.read('.sdd/critique-package-2.json')
        r = self.result(False)
        self.assertEqual(self.cli('critique-import', code=3)['reason'], 'CRITIQUE_IDENTITY_MISMATCH')
        r.update({k: p[k] for k in ('package_id', 'subject', 'contract_id', 'prompt_id')})
        self.json('.sdd/critic-result.json', r)
        self.cli('critique-import')
        self.json('.sdd/dispositions.json', {'schema': 1, 'subject': p['subject'], 'findings': {}})
        self.assertEqual(self.cli('critique-dispose', '--by', 'owner', code=3)['reason'], 'MISSING_FINDING_RESOLUTIONS')
        self.assertEqual(self.cli('critique-prepare', code=3)['reason'], 'REVIEW_BUDGET_EXHAUSTED')

    def test_missing_ledger_and_duplicate_json_fail_closed(self):
        self.prepare()
        self.result()
        text = (self.root / '.sdd/critic-result.json').read_text()
        self.put('.sdd/critic-result.json', text[:-1] + ', "schema": 1}')
        self.assertEqual(self.cli('critique-import', code=3)['reason'], 'DUPLICATE_JSON_KEY')
        state = self.read('.sdd/state.json')
        del state['critique']
        self.json('.sdd/state.json', state)
        self.cli('finish', code=3)

    def test_package_bound_and_symlink(self):
        self.put('big.txt', 'x' * 2097153)
        self.cli('check')
        self.assertEqual(self.cli('critique-prepare', code=3)['reason'], 'CRITIQUE_PACKAGE_BYTE_LIMIT')
        (self.root / 'big.txt').unlink()
        (self.root / 'link').symlink_to('app.py')
        self.cli('check')
        self.assertEqual(self.cli('critique-prepare', code=3)['reason'], 'SYMLINK_INPUT')
        self.assertEqual(self.read('.sdd/state.json')['critique']['reviews'], 0)

    def test_pending_note_edit_blocks_import_without_spending(self):
        self.prepare()
        self.result()
        original = (self.root / 'review.md').read_text()
        self.put('review.md', 'Premature review note edit\n')
        self.assertEqual(self.cli('critique-import', code=3)['reason'], 'STALE_EVIDENCE')
        self.assertEqual(self.cli('check', code=3)['reason'], 'IMPORT_BEFORE_REPAIR')
        self.assertEqual(self.read('.sdd/state.json')['critique']['repairs'], 0)
        self.put('review.md', original)
        self.cli('critique-import')

    def test_pending_protected_amendment_cannot_erase_review(self):
        self.prepare()
        self.put('test_app.py', (self.root / 'test_app.py').read_text() + '# changed oracle\n')
        self.assertEqual(self.cli('check', code=3)['reason'], 'AMENDMENT_REQUIRED')
        self.assertEqual(self.cli('change', '--accept', 'owner', '--reason', 'oracle update', code=3)['reason'], 'CRITIQUE_ACTIVE_AMENDMENT_BLOCKED')
        self.assertEqual(self.read('.sdd/state.json')['critique']['reviews'], 1)

    def test_non_object_result_and_disposition_fail_closed(self):
        self.prepare()
        for value in (None, [], True, 1, 'result'):
            self.json('.sdd/critic-result.json', value)
            self.cli('critique-import', code=3)
        self.result(False)
        self.cli('critique-import')
        for value in (None, [], True, 1, 'disposition'):
            self.json('.sdd/dispositions.json', value)
            self.cli('critique-dispose', '--by', 'owner', code=3)
        self.assertEqual(self.cli('finish', code=3)['reason'], 'FINDINGS_DISPOSITION_REQUIRED')

    def test_redisposition_invalidates_prior_manual_acceptance(self):
        self.imported(False)
        self.json('.sdd/dispositions.json', {'schema': 1, 'subject': self.read('.sdd/receipt.json')['identity'], 'findings': {}})
        self.cli('critique-dispose', '--by', 'owner')
        self.cli('review', '--by', 'scripted-not-human', '--evidence', 'review.md')
        self.cli('finish')
        self.cli('critique-dispose', '--by', 'another-owner')
        self.assertFalse((self.root / '.sdd/finish.json').exists())
        self.assertEqual(self.cli('finish', code=3)['reason'], 'MANUAL_REVIEW_REQUIRED')

    def test_ignored_brief_still_packaged_and_pinned(self):
        self.put('.gitignore', '.sdd/\n__pycache__/\nbrief.md\n')
        self.cli('check')
        p = self.prepare()
        self.assertEqual(base64.b64decode(p['source']['brief.md']['base64']), (self.root / 'brief.md').read_bytes())
        self.put('brief.md', 'Unauthorized replacement')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'AMENDMENT_REQUIRED')

    def test_lost_disposition(self):
        self.imported(False)
        self.json('.sdd/dispositions.json', {'schema': 1, 'subject': self.read('.sdd/receipt.json')['identity'], 'findings': {}})
        self.cli('critique-dispose', '--by', 'owner')
        self.cli('review', '--by', 'owner', '--evidence', 'review.md')
        self.put('.sdd/critique-disposition.json', '{}')
        self.assertEqual(self.cli('finish', code=3)['reason'], 'LOST_CRITIQUE_ARTIFACT')


if __name__ == '__main__':
    unittest.main()
