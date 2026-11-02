"""Real Git/test lifecycle; scripted agents, local transport only."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_pipeline
from coordinator import Coordinator
from controller import Controller, evo


class Tasks(unittest.TestCase):
    setUp = test_pipeline.Pipeline.setUp
    tearDown = test_pipeline.Pipeline.tearDown
    git = test_pipeline.Pipeline.git

    def setup_task(self, adapter='fixture'):
        self.c.db.close()
        self.c = Controller(self.root / 'state')
        self.cfg['adapter'] = adapter
        self.c.configure(self.cfg)
        self.q = Coordinator(self.c)
        self.q.configure(dict(tenant=self.cfg['profile'], repo=str(self.repo), stall_seconds=1,
                              routes=[dict(source='local', thread='test-thread', authors=['operator'],
                                           destination={'kind': 'local', 'path': str(self.root / 'sink')})]))
        self.e = dict(event_id='event-1', source='local', thread='test-thread', author='operator', session_id='session-1',
                      tenant=self.cfg['profile'], repo=str(self.repo), kind='submit', objective='Implement addition.',
                      provenance={'verification': 'local-operator', 'uid': os.getuid()})
        return self.q.ingest(self.e)

    def revision(self, t):
        return dict(self.e, event_id='revision-1', kind='revise', task_id=t['id'], objective='Add numbers while preserving name.')

    def test_submit_nonblocking_restart_run_verified_delivery(self):
        t = self.setup_task()
        self.assertIsNone(t['run_id'])
        self.c.db.close()
        self.c = Controller(self.root / 'state'); self.q = Coordinator(self.c)
        with self.c.lock():
            t = self.q.tick()[0]
            self.assertNotEqual(t['run_id'], t['id'])
            t = self.q.run(t['id'])
        self.assertEqual(t['state'], 'pr-ready')
        self.assertEqual(t['progress']['check_rounds'], 2)
        self.assertFalse(t['accepted']); self.assertFalse(t['released'])
        self.assertIsNotNone(t['last_verified'])
        self.assertIn('manual', t['next_step'])
        self.assertTrue(self.q.deliver()['local_delivered'])
        self.assertTrue(self.q.task(t['id'])['notified'])
        self.assertEqual(self.q.deliver()['local_delivered'], [])
        self.assertIn('FAILED', (self.c.root / t['run_id'] / 'check-1-0.log').read_text())
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_dedupe_conflict_and_immutable_objective(self):
        t = self.setup_task()
        self.assertEqual(self.q.ingest(self.e)['id'], t['id'])
        with self.assertRaisesRegex(evo.Blocked, 'EVENT_CONFLICT'):
            self.q.ingest(dict(self.e, objective='different'))
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.db.execute('UPDATE objectives SET data=?', ('{}',))
        self.c.db.rollback()
        self.assertEqual(self.q.objective(t)['objective'], 'Implement addition.')

    def test_boundary_rejects_without_side_effect(self):
        t = self.setup_task()
        for change in ({'tenant': 'other'}, {'repo': '/tmp/other'}, {'author': 'stranger'}, {'thread': 'other'},
                       {'source': 'telegram'}, {'provenance': {'verified': True}}):
            with self.subTest(change=change), self.assertRaises(evo.Blocked):
                self.q.ingest(dict(self.e, event_id='bad', **change))
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM ingress').fetchone()[0], 1)
        with self.assertRaisesRegex(evo.Blocked, 'TASK_BOUNDARY'):
            # Valid second route does not grant ownership of first task.
            p = self.q.policy(); p['routes'].append(dict(source='local', thread='other', authors=['operator'], destination=p['routes'][0]['destination']))
            self.c.db.execute('UPDATE coordinator_policy SET data=?', (json.dumps(p),)); self.c.db.commit()
            self.q.ingest(dict(self.e, event_id='new', kind='status', task_id=t['id'], thread='other'))

    def test_thread_resolution_explicit_and_ambiguous(self):
        t = self.setup_task()
        e = dict(self.e, event_id='status', kind='status')
        self.assertEqual(self.q.ingest(e)['id'], t['id'])
        self.q.ingest(dict(self.e, event_id='second'))
        with self.assertRaisesRegex(evo.Blocked, 'EXPLICIT_TASK_ID_REQUIRED'):
            self.q.ingest(dict(e, event_id='status-2'))
        self.assertEqual(self.q.ingest(dict(e, event_id='status-3', task_id=t['id']))['id'], t['id'])

    def test_revision_cancels_before_replacement_and_preserves_original(self):
        t = self.setup_task('external'); t = self.q.tick()[0]
        old = t['run_id']; self.q.run(t['id'])
        self.q.ingest(self.revision(t))
        with self.assertRaisesRegex(evo.Blocked, 'TICK_OR_REVISION_REQUIRED'): self.q.run(t['id'])
        t = self.q.tick()[0]
        self.assertEqual(self.c.job(old)['state'], 'cancelled')
        self.assertNotEqual(old, t['run_id']); self.assertEqual(t['version'], 2)
        original = json.loads(self.c.db.execute('SELECT data FROM objectives WHERE task=? AND version=1', (t['id'],)).fetchone()[0])
        self.assertEqual(original['objective'], self.e['objective'])
        self.assertEqual(self.q.objective(t)['author'], 'operator')

    def test_revision_waits_for_ambiguous_effect_reconciliation(self):
        t = self.setup_task(); t = self.q.tick()[0]; old = t['run_id']
        j = self.c.job(old); j['completed_effect'] = {'label': 'test'}; self.c.save(j)
        self.q.ingest(self.revision(t)); t = self.q.tick()[0]
        self.assertEqual(t['run_id'], old); self.assertEqual(t['version'], 1)
        self.assertIn('OLD_RUN_REQUIRES_CANCEL_AND_RECONCILE', t['blockers'])
        self.c.drive(j); self.assertEqual(j['state'], 'reconcile-required')
        j.update(state='needs-human', reconciliation='Operator inspected and stopped'); self.c.save(j)
        t = self.q.tick()[0]
        self.assertNotEqual(t['run_id'], old); self.assertEqual(self.c.job(old)['state'], 'cancelled')

    def test_cancel_does_not_erase_partial_apply_revision_barrier(self):
        t = self.setup_task('external'); t = self.q.tick()[0]
        self.q.run(t['id'])
        j = self.c.job(t['run_id'])
        # Crash after persisting apply intent, before completion; no subprocess marker.
        j['state'] = 'applying'; self.c.save(j)
        self.c.cancel(j['id'])
        self.q.ingest(self.revision(t))
        observed = self.q.tick()[0]
        self.assertEqual(observed['run_id'], j['id'])
        self.assertEqual(observed['version'], 1)
        self.assertIn('OLD_RUN_REQUIRES_CANCEL_AND_RECONCILE', observed['blockers'])

    def test_crash_after_start_before_link_reuses_job(self):
        t = self.setup_task()
        with patch.object(self.q, 'notify', side_effect=RuntimeError('simulated crash boundary')):
            with self.assertRaises(RuntimeError): self.q.tick()
        jobs = self.c.db.execute("SELECT id FROM jobs WHERE id!='config'").fetchall()
        self.assertEqual(len(jobs), 1)
        self.c.db.close(); self.c = Controller(self.root / 'state'); self.q = Coordinator(self.c)
        self.assertEqual(self.q.tick()[0]['run_id'], jobs[0][0])
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM jobs WHERE id!='config'").fetchone()[0], 1)

    def test_actual_process_exit_rolls_back_ingress_transaction(self):
        self.setup_task()
        code = "import sqlite3,os; d=sqlite3.connect(__import__('sys').argv[1]); d.execute(\"INSERT INTO ingress VALUES('local','crashed','x','none')\"); os._exit(71)"
        r = subprocess.run([sys.executable, '-c', code, str(self.c.root / 'jobs.db')])
        self.assertEqual(r.returncode, 71)
        self.assertIsNone(self.c.db.execute("SELECT 1 FROM ingress WHERE event='crashed'").fetchone())
        self.q.ingest(dict(self.e, event_id='crashed'))

    def test_sink_written_before_ack_replays_without_duplicate(self):
        self.setup_task(); t = self.q.tick()[0]
        row = self.c.db.execute('SELECT id,data FROM outbox').fetchone()
        dest = self.root / 'sink'; dest.mkdir(mode=0o700)
        (dest / (row[0] + '.json')).write_text(row[1])  # previous process died after durable delivery
        self.q.deliver(); self.q.tick(); self.q.deliver()
        self.assertEqual(len(list(dest.glob('*.json'))), 1)
        self.assertTrue(self.q.task(t['id'])['notified'])

    def test_sink_conflict_and_symlink_fail_closed(self):
        self.setup_task(); self.q.tick()
        oid = self.c.db.execute('SELECT id FROM outbox').fetchone()[0]
        dest = self.root / 'sink'; dest.mkdir(mode=0o700); f = dest / (oid + '.json'); f.write_text('wrong')
        with self.assertRaisesRegex(evo.Blocked, 'DELIVERY_CONFLICT'): self.q.deliver()
        f.unlink(); f.symlink_to(self.repo / 'calc.py')
        with self.assertRaisesRegex(evo.Blocked, 'DELIVERY_SYMLINK'): self.q.deliver()
        self.assertIsNone(self.c.db.execute('SELECT delivered FROM outbox').fetchone()[0])

    def test_watchdog_stall_budget_and_unreviewed_no_model_call(self):
        t = self.setup_task('external'); t = self.q.tick()[0]; j = self.c.job(t['run_id'])
        with patch('coordinator.time.time', return_value=j['created'] + 1000):
            t = self.q.tick()[0]
        self.assertIn('WALLTIME_LIMIT', t['blockers']); self.assertIn('MISSING_WORKER_OR_STALLED', t['blockers'])
        self.q.run(t['id']); j = self.c.job(t['run_id'])
        r = j['request']; result = {k: r[k] for k in ('schema', 'job', 'role', 'nonce', 'source')}
        self.c.import_result(j, dict(result, edits={'calc.py': 'def add(a,b):\n    return a+b\n'})); self.c.drive(j)
        with patch('coordinator.time.time', return_value=j['updated'] + 2): t = self.q.tick()[0]
        self.assertIn('RESULTS_UNREVIEWED', t['blockers']); self.assertEqual(t['state'], 'waiting-critic')
        self.assertFalse(t['accepted'])

    def test_evidence_tamper_invalidates_completion(self):
        t = self.setup_task(); self.q.tick(); t = self.q.run(t['id'])
        (self.c.workspace(self.c.job(t['run_id'])) / 'calc.py').write_text('bad')
        t = self.q.tick()[0]
        self.assertEqual(t['state'], 'evidence-invalid'); self.assertIn('STALE_EVIDENCE', t['blockers'])

    def test_completion_delivery_revalidates_and_suppresses_stale_alert(self):
        t = self.setup_task(); self.q.tick(); t = self.q.run(t['id'])
        (self.c.workspace(self.c.job(t['run_id'])) / 'calc.py').write_text('bad')
        self.q.deliver()
        payloads = [json.loads(p.read_text()) for p in (self.root / 'sink').glob('*.json')]
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0]['status']['state'], 'evidence-invalid')

    def test_busy_controller_exclusion(self):
        self.setup_task()
        with self.c.lock():
            r = subprocess.run([sys.executable, str(Path(__file__).with_name('coordinator.py')), '--state', str(self.c.root), 'tick'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2); self.assertIn('CONTROLLER_BUSY', r.stderr)

    def test_status_cli_and_separate_process_dedupe(self):
        t = self.setup_task(); f = self.root / 'event.json'; f.write_text(json.dumps(self.e))
        cmd = [sys.executable, str(Path(__file__).with_name('coordinator.py')), '--state', str(self.c.root)]
        r = subprocess.run(cmd + ['ingest', str(f)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(json.loads(r.stdout)['id'], t['id'])
        r = subprocess.run(cmd + ['status', t['id']], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertEqual(json.loads(r.stdout)['state'], 'queued')


if __name__ == '__main__': unittest.main()
