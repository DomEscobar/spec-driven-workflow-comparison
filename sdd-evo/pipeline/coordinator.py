#!/usr/bin/env python3
"""Local task ledger in the existing pipeline DB; no daemon or network ingress."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid
from controller import Controller, TERMINAL, evo, require, redact


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


class Coordinator:
    def __init__(self, controller):
        self.c = controller
        self.db = controller.db
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS coordinator_policy(id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS objectives(task TEXT, version INTEGER, data TEXT NOT NULL, PRIMARY KEY(task,version));
        CREATE TABLE IF NOT EXISTS ingress(source TEXT, event TEXT, digest TEXT NOT NULL, task TEXT NOT NULL, PRIMARY KEY(source,event));
        CREATE TABLE IF NOT EXISTS task_events(id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, task TEXT NOT NULL, fingerprint TEXT NOT NULL, data TEXT NOT NULL, delivered REAL, UNIQUE(task,fingerprint));
        CREATE TRIGGER IF NOT EXISTS objective_no_update BEFORE UPDATE ON objectives BEGIN SELECT RAISE(ABORT,'immutable objective'); END;
        CREATE TRIGGER IF NOT EXISTS objective_no_delete BEFORE DELETE ON objectives BEGIN SELECT RAISE(ABORT,'immutable objective'); END;
        CREATE TRIGGER IF NOT EXISTS event_no_update BEFORE UPDATE ON task_events BEGIN SELECT RAISE(ABORT,'immutable event'); END;
        CREATE TRIGGER IF NOT EXISTS event_no_delete BEFORE DELETE ON task_events BEGIN SELECT RAISE(ABORT,'immutable event'); END;
        ''')

    def configure(self, policy):
        require(not self.db.execute('SELECT 1 FROM coordinator_policy').fetchone(), 'ALREADY_CONFIGURED')
        cfg = self.c.config()
        require(policy.get('tenant') == cfg['profile'] and policy.get('repo') == cfg['repo'], 'POLICY_SCOPE')
        require(isinstance(policy.get('stall_seconds'), int) and 1 <= policy['stall_seconds'] <= 86400, 'STALL_BUDGET')
        routes = policy.get('routes')
        require(isinstance(routes, list) and routes, 'ROUTES_REQUIRED')
        keys = set()
        for route in routes:
            require(set(route) == {'source', 'thread', 'authors', 'destination'}, 'ROUTE_SCHEMA')
            require(route['source'] == 'local' and isinstance(route['thread'], str) and route['thread'], 'LOCAL_ONLY')
            require(isinstance(route['authors'], list) and route['authors'] and all(isinstance(x, str) and x for x in route['authors']), 'AUTHORS_REQUIRED')
            key = (route['source'], route['thread'])
            require(key not in keys, 'AMBIGUOUS_ROUTE'); keys.add(key)
            dest = route['destination']
            require(set(dest) == {'kind', 'path'} and dest['kind'] == 'local', 'LOCAL_DELIVERY_ONLY')
            path = Path(dest['path'])
            require(path.is_absolute() and str(path.resolve()) == str(path) and not path.is_relative_to(Path(cfg['repo'])), 'DESTINATION_PATH')
            require(not path.exists() or (path.is_dir() and path.stat().st_uid == os.getuid()), 'DESTINATION_OWNER')
        policy = dict(policy, runtime=evo.filehash(Path(__file__)))
        with self.db:
            self.db.execute('INSERT INTO coordinator_policy VALUES(1,?)', (canonical(policy),))
        return {'configured': True, 'transport': 'local-only'}

    def policy(self):
        row = self.db.execute('SELECT data FROM coordinator_policy WHERE id=1').fetchone()
        require(row, 'COORDINATOR_NOT_CONFIGURED')
        p = json.loads(row[0])
        c = self.c.config()
        require(p['tenant'] == c['profile'] and p['repo'] == c['repo'], 'POLICY_SCOPE')
        require(p['runtime'] == evo.filehash(Path(__file__)), 'COORDINATOR_RUNTIME_CHANGED')
        return p

    def task(self, tid):
        row = self.db.execute('SELECT data FROM tasks WHERE id=?', (tid,)).fetchone()
        require(row, 'NO_TASK')
        t = json.loads(row[0])
        p = self.policy()
        require(t['tenant'] == p['tenant'] and t['repo'] == p['repo'], 'TASK_SCOPE')
        return t

    def save(self, t):
        self.db.execute('INSERT OR REPLACE INTO tasks VALUES(?,?)', (t['id'], canonical(t)))

    def event(self, tid, kind, data):
        self.db.execute('INSERT INTO task_events(task,kind,data) VALUES(?,?,?)', (tid, kind, canonical(data)))

    def ingest(self, e):
        """Caller is the trusted local operator, not a remote transport authentication service."""
        p = self.policy()
        required = {'event_id', 'source', 'thread', 'author', 'session_id', 'tenant', 'repo', 'kind', 'provenance'}
        require(required <= set(e) and set(e) <= required | {'task_id', 'objective', 'evidence_requirement'}, 'EVENT_SCHEMA')
        require(all(isinstance(e[k], str) and e[k] and len(e[k]) <= 16000 for k in required - {'provenance'}), 'EVENT_FIELDS')
        require(e['source'] == 'local' and e['provenance'] == {'verification': 'local-operator', 'uid': os.getuid()}, 'UNVERIFIED_SOURCE')
        require(e['tenant'] == p['tenant'] and e['repo'] == p['repo'], 'INGRESS_SCOPE')
        route = next((r for r in p['routes'] if r['source'] == e['source'] and r['thread'] == e['thread']), None)
        require(route and e['author'] in route['authors'], 'UNAUTHORIZED_ROUTE')
        digest = evo.digest(e)
        old = self.db.execute('SELECT digest,task FROM ingress WHERE source=? AND event=?', (e['source'], e['event_id'])).fetchone()
        if old:
            require(old[0] == digest, 'EVENT_CONFLICT')
            return self.task(old[1])
        require(e['kind'] in ('submit', 'revise', 'status'), 'EVENT_KIND')
        tid = e.get('task_id')
        if e['kind'] == 'submit':
            require(not tid, 'NEW_TASK_ID_IS_ASSIGNED')
            tid = uuid.uuid4().hex
            t = dict(id=tid, tenant=p['tenant'], repo=p['repo'], source=e['source'], thread=e['thread'],
                     owner=e['author'], version=1, run_id=None, runs=[], state='submitted',
                     next_step='tick to allocate run', evidence_requirement=e.get('evidence_requirement', 'protected tests and independent critic; manual acceptance separately'),
                     last_verified=None, progress={}, blockers=[], notified=False, destination=route['destination'],
                     accepted=False, released=False, created=time.time())
        else:
            if not tid:
                rows = [json.loads(x[0]) for x in self.db.execute('SELECT data FROM tasks')]
                matches = [x for x in rows if x['source'] == e['source'] and x['thread'] == e['thread']]
                require(len(matches) == 1, 'EXPLICIT_TASK_ID_REQUIRED')
                tid = matches[0]['id']
            t = self.task(tid)
            require(t['source'] == e['source'] and t['thread'] == e['thread'] and t['owner'] == e['author'], 'TASK_BOUNDARY')
        if e['kind'] in ('submit', 'revise'):
            require(isinstance(e.get('objective'), str) and e['objective'].strip() and len(e['objective'].encode()) <= 16000, 'OBJECTIVE_REQUIRED')
            require(isinstance(t['evidence_requirement'], str) and t['evidence_requirement'].strip(), 'EVIDENCE_REQUIRED')
        with self.db:
            if e['kind'] == 'revise':
                require(not t.get('pending_revision'), 'REVISION_PENDING')
                # Persist cancellation intent with accepted revision. Tick cannot allocate replacement
                # until the old job is stopped without ambiguous effects, or explicitly reconciled.
                t['pending_revision'] = dict(objective=e['objective'], author=e['author'], event_id=e['event_id'], session_id=e['session_id'])
                t.update(state='revision-pending', next_step='stop/reconcile old run before replacement', notified=False)
                if t['run_id']:
                    self.db.execute('UPDATE jobs SET cancel=1 WHERE id=?', (t['run_id'],))
            elif e['kind'] == 'submit':
                self.db.execute('INSERT INTO objectives VALUES(?,?,?)', (tid, 1, canonical(dict(objective=e['objective'], author=e['author'], event_id=e['event_id'], session_id=e['session_id']))))
            t['last_session_id'] = e['session_id']
            self.save(t)
            self.db.execute('INSERT INTO ingress VALUES(?,?,?,?)', (e['source'], e['event_id'], digest, tid))
            self.event(tid, 'ingress:' + e['kind'], e)
        return t

    def objective(self, t):
        return json.loads(self.db.execute('SELECT data FROM objectives WHERE task=? AND version=?', (t['id'], t['version'])).fetchone()[0])

    def notify(self, t):
        # Exclude observation timestamps: periodic ticks must not multiply identical alerts.
        view = {k: t[k] for k in ('id', 'version', 'run_id', 'state', 'next_step', 'progress', 'blockers', 'accepted', 'released')}
        fingerprint = evo.digest(view)
        oid = evo.digest([t['id'], fingerprint])
        payload = dict(id=oid, task_id=t['id'], destination=t['destination'], status=view)
        self.db.execute('INSERT OR IGNORE INTO outbox VALUES(?,?,?,?,NULL)', (oid, t['id'], fingerprint, canonical(payload)))
        t['notification_id'] = oid
        row = self.db.execute('SELECT delivered FROM outbox WHERE id=?', (oid,)).fetchone()
        t['notified'] = row[0] is not None

    def tick(self):
        p = self.policy()
        results = []
        for (tid,) in self.db.execute('SELECT id FROM tasks ORDER BY id').fetchall():
            t = self.task(tid)
            j = self.c.job(t['run_id']) if t['run_id'] else None
            if t.get('pending_revision'):
                if j:
                    ambiguous = j.get('inflight') or j.get('completed_effect') or j['state'] in ('cloning', 'applying', 'publishing', 'reconcile-required')
                    reconciled = j['state'] == 'needs-human' and j.get('reconciliation')
                    if ambiguous and not reconciled:
                        t.update(state='revision-pending', blockers=['OLD_RUN_REQUIRES_CANCEL_AND_RECONCILE'], next_step='controller cancel; resume to expose reconciliation; reconcile --inspected-and-stopped')
                        with self.db:
                            self.notify(t); self.save(t)
                        results.append(t); continue
                    # Same exclusive controller lock: no runner can race this transition.
                    j['state'] = 'cancelled'; self.c.save(j)
                with self.db:
                    t['version'] += 1
                    self.db.execute('INSERT INTO objectives VALUES(?,?,?)', (tid, t['version'], canonical(t.pop('pending_revision'))))
                    t.update(run_id=None, accepted=False, released=False, last_verified=None, progress={}, blockers=[])
                    self.event(tid, 'revision-activated', {'version': t['version'], 'cancelled_run': j['id'] if j else None})
                    self.save(t)
                j = None
            if not j:
                # start is already durable/idempotent. Crash before task linkage reuses this exact job.
                j = self.c.start(self.objective(t)['objective'], 'coordinator:' + tid + ':' + str(t['version']))
                t['run_id'] = j['id']
                if j['id'] not in t['runs']: t['runs'].append(j['id'])
            t['blockers'] = []
            try:
                self.c.guard(j)
                t['last_verified'] = time.time()
                t['progress'] = dict(check_rounds=j['runs'], reviews=j['reviews'], repairs=j['repairs'], checks=j.get('checks', []))
                t['state'] = j['state']
                t['next_step'] = {'queued': 'run task explicitly', 'waiting-builder': 'delegate current builder request',
                                  'waiting-critic': 'delegate fresh independent critic request', 'pr-ready': 'manual review/acceptance required; not released',
                                  'needs-human': 'operator review required', 'published': 'draft PR only; manual acceptance/release separate'}.get(j['state'], 'inspect and resume run')
                if j.get('inflight') or j.get('completed_effect') or j['state'] in ('cloning', 'applying', 'publishing', 'reconcile-required'):
                    t['blockers'].append('RECONCILE_REQUIRED')
                if j['state'] not in TERMINAL:
                    reason = self.c.stop_reason(j)
                    if reason: t['blockers'].append(reason)
                    if time.time() - j.get('updated', j['created']) >= p['stall_seconds']:
                        t['blockers'].append('RESULTS_UNREVIEWED' if j['state'] in ('review', 'waiting-critic') else 'MISSING_WORKER_OR_STALLED')
                if j.get('error'): t['blockers'].append(j['error'])
            except (evo.Blocked, OSError, ValueError) as exc:
                t.update(state='evidence-invalid', blockers=[str(exc)], next_step='inspect evidence; no completion claim')
            with self.db:
                self.notify(t); self.save(t)
                self.event(tid, 'verified-observation', {k: t[k] for k in ('run_id', 'state', 'last_verified', 'blockers')})
            results.append(t)
        return results

    def run(self, tid):
        t = self.task(tid)
        require(t['run_id'] and not t.get('pending_revision'), 'TICK_OR_REVISION_REQUIRED')
        j = self.c.job(t['run_id'])
        try:
            self.c.drive(j)
        except (evo.Blocked, ValueError, OSError) as exc:
            self.c.fail(j, exc)
        self.tick()
        return self.task(tid)

    def deliver(self):
        """Idempotent local file sink. No Telegram/GitHub acknowledgement is fabricated."""
        self.tick()  # Revalidate before emitting a completion; do not deliver stale queued statuses.
        delivered = []
        for oid, tid, data in self.db.execute('SELECT id,task,data FROM outbox WHERE delivered IS NULL ORDER BY rowid').fetchall():
            if self.task(tid).get('notification_id') != oid:
                continue  # Superseded record retained for audit, not represented as delivered.
            payload = json.loads(data)
            dest = Path(payload['destination']['path'])
            require(str(dest.resolve()) == str(dest), 'DESTINATION_SYMLINK')
            dest.mkdir(mode=0o700, parents=True, exist_ok=True)
            require(dest.stat().st_uid == os.getuid() and not dest.stat().st_mode & 0o022, 'DESTINATION_PERMISSIONS')
            final = dest / (oid + '.json')
            require(not final.is_symlink(), 'DELIVERY_SYMLINK')
            if not final.exists():
                # Publish a fully fsynced file without overwriting an existing receipt.
                temp = dest / ('.' + uuid.uuid4().hex)
                try:
                    with temp.open('x') as f:
                        os.chmod(temp, 0o600); f.write(data); f.flush(); os.fsync(f.fileno())
                    try: os.link(temp, final)
                    except FileExistsError: pass
                finally: temp.unlink(missing_ok=True)
            require(final.is_file() and final.read_text() == data, 'DELIVERY_CONFLICT')
            fd = os.open(dest, os.O_RDONLY)
            try: os.fsync(fd)
            finally: os.close(fd)
            # Crash here is safe: next tick reads the identical destination and acknowledges once.
            with self.db:
                self.db.execute('UPDATE outbox SET delivered=? WHERE id=?', (time.time(), oid))
                t = self.task(tid)
                if t.get('notification_id') == oid: t['notified'] = True; self.save(t)
                self.event(tid, 'local-delivery', {'notification_id': oid, 'destination': payload['destination']})
            delivered.append(oid)
        return {'local_delivered': delivered, 'remote_delivery': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state', required=True)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('configure', 'ingest'):
        sub.add_parser(name).add_argument('file', type=Path)
    s = sub.add_parser('submit'); s.add_argument('requirement'); s.add_argument('--thread', required=True); s.add_argument('--author', required=True); s.add_argument('--session', required=True); s.add_argument('--event', required=True)
    for name in ('status', 'run'): sub.add_parser(name).add_argument('task')
    for name in ('tick', 'deliver', 'outbox'): sub.add_parser(name)
    a = p.parse_args()
    c = Controller(a.state)
    try:
        with c.lock():
            q = Coordinator(c)
            if a.cmd == 'configure': result = q.configure(evo.load(a.file))
            elif a.cmd == 'ingest': result = q.ingest(evo.load(a.file))
            elif a.cmd == 'submit':
                policy = q.policy()
                result = q.ingest(dict(event_id=a.event, source='local', thread=a.thread, author=a.author, session_id=a.session,
                                      tenant=policy['tenant'], repo=policy['repo'], kind='submit', objective=a.requirement,
                                      provenance={'verification': 'local-operator', 'uid': os.getuid()}))
            elif a.cmd == 'tick': result = q.tick()
            elif a.cmd == 'deliver': result = q.deliver()
            elif a.cmd == 'run': result = q.run(a.task)
            elif a.cmd == 'status':
                q.tick(); result = q.task(a.task)
            else:
                q.policy(); result = [dict(json.loads(d), delivered=at) for d, at in q.db.execute('SELECT data,delivered FROM outbox ORDER BY rowid')]
        print(json.dumps(result, indent=2))
        return 0
    except (evo.Blocked, ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': redact(str(exc))}), file=sys.stderr)
        return 2
    finally: c.db.close()


if __name__ == '__main__': sys.exit(main())
