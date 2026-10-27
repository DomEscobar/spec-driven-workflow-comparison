#!/usr/bin/env python3
"""Disposable real Git + Python app, real CLI fail/fix/pass/stale walkthrough."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

CLI = Path(__file__).resolve().parents[1] / 'evo.py'


def main():
    with tempfile.TemporaryDirectory(prefix='evo-example-') as temp:
        root = Path(temp)
        def put(name, text):
            (root / name).write_text(text)
        def run(*args, expected=0):
            result = subprocess.run([sys.executable, str(CLI), '--repo', temp, *args], capture_output=True, text=True)
            print('evo ' + ' '.join(args) + f' -> exit {result.returncode}')
            print(result.stdout.strip())
            if result.returncode != expected:
                raise RuntimeError(result.stderr or result.stdout)
        put('.gitignore', '.sdd/\n__pycache__/\n')
        put('app.py', 'def add(a, b): return a - b\n')
        put('test_app.py', 'import unittest\nfrom app import add\nclass Test(unittest.TestCase):\n def test_add(self): self.assertEqual(add(2, 3), 5)\n')
        # Explicit example review, not a claim about a real human inspecting this app.
        put('review.md', 'Example fixture review: addition requirement; no UI. Not independent approval.\n')
        for args in [('init', '-q'), ('add', '.'), ('-c', 'user.name=Evo example', '-c', 'user.email=example@invalid', 'commit', '-qm', 'seed bug')]:
            subprocess.run(['git', '-C', temp, *args], check=True, capture_output=True)
        run('init')
        contract = json.loads((root / 'evo-contract.json').read_text())
        contract.update(outcome='Add two numbers', requirements={'R1': '2 + 3 returns 5'}, accepted_basis='Explicit local walkthrough')
        put('evo-contract.json', json.dumps(contract))
        run('start', '--accept', 'example-owner')
        run('check', expected=3)
        receipt = json.loads((root / '.sdd/receipt.json').read_text())
        assert receipt['results']['unit']['exit_code'] != 0
        put('app.py', 'def add(a, b): return a + b\n')
        run('check')
        run('review', '--by', 'example-reviewer', '--evidence', 'review.md')
        run('finish')
        put('app.py', 'def add(a, b): return 0\n')
        run('finish', expected=3)
        print('Walkthrough verified: real failing test -> real fix -> local finish -> stale rejected. No release.')


if __name__ == '__main__':
    main()
