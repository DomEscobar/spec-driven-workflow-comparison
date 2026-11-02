#!/usr/bin/env python3
"""Disposable real Git demo, no inference. --adapter external exposes parent-worker protocol."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from controller import Controller, git


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    p.add_argument('--adapter', choices=['fixture', 'external'], default='fixture')
    p.add_argument('--image', help='optional locally present sha256 Docker image; never pulled')
    p.add_argument('--coordinator', action='store_true', help='exercise task ledger and explicit local delivery')
    a = p.parse_args()
    root = a.directory.resolve()
    if root.exists():
        p.error('Use a new directory; existing data is never overwritten.')
    repo = root / 'repo'; repo.mkdir(parents=True)
    git(repo, 'init', '-q')
    git(repo, 'config', 'user.email', 'fixture@example.invalid')
    git(repo, 'config', 'user.name', 'SDD-evo deterministic demo')
    (repo / 'calc.py').write_text('def add(a, b):\n    return 0\n')
    (repo / 'test_calc.py').write_text('import unittest\nfrom calc import add\nclass Addition(unittest.TestCase):\n    def test_add(self): self.assertEqual(add(2,3),5)\n')
    git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'Disposable demo baseline')
    cfg = dict(repo=str(repo), profile='demo', project='addition', trusted_repo=True, risk='low',
               adapter=a.adapter, fixture_only=True, worker=str(Path(__file__).with_name('fixture_worker.py')),
               allowed_files=['calc.py'], protected_files=['test_calc.py'],
               execution='docker' if a.image else 'trusted-local',
               checks=[{'argv': ['/opt/hermes/.venv/bin/python3' if a.image else sys.executable, '-m', 'unittest', 'discover', '-v'], 'min_tests': 1}])
    if a.image: cfg['image'] = a.image
    (root / 'policy.json').write_text(json.dumps(cfg, indent=2))
    requirement = 'Implement add(a,b) so it returns the sum of the two numbers. Preserve the public function name.'
    (root / 'requirement.txt').write_text(requirement)
    c = Controller(root / 'state')
    try:
        with c.lock():
            c.configure(cfg)
            task = None
            if a.coordinator:
                from coordinator import Coordinator
                import os
                q = Coordinator(c)
                q.configure(dict(tenant=cfg['profile'], repo=str(repo), stall_seconds=300,
                                 routes=[dict(source='local', thread='demo', authors=['demo-operator'],
                                              destination={'kind': 'local', 'path': str(root / 'local-delivery')})]))
                task = q.ingest(dict(event_id='demo-1', source='local', thread='demo', author='demo-operator',
                                     session_id='demo-session', tenant=cfg['profile'], repo=str(repo), kind='submit',
                                     objective=requirement, provenance={'verification': 'local-operator', 'uid': os.getuid()}))
                q.tick()
                task = q.run(task['id'])
                q.deliver()
                task = q.task(task['id'])
                j = c.job(task['run_id'])
            else:
                j = c.start(requirement, 'addition-1')
                c.drive(j)
        result = {k: j[k] for k in ('id', 'state', 'runs', 'repairs', 'reviews')}
        if task:
            result.update(task_id=task['id'], local_notified=task['notified'], accepted=task['accepted'], released=task['released'])
        result.update(adapter=a.adapter, model_execution=False, state_directory=str(c.root),
                      artifacts=str(c.root / j['id']), workspace=str(c.workspace(j)))
        print(json.dumps(result, indent=2))
    finally: c.db.close()


if __name__ == '__main__': main()
