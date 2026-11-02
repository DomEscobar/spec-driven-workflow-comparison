#!/usr/bin/env python3
"""DETERMINISTIC TEST DOUBLE. No model, no human, no effectiveness evidence."""
import json
from pathlib import Path
import sys
r = json.loads(Path(sys.argv[1]).read_text())
a = {k: r[k] for k in ('schema', 'job', 'role', 'nonce', 'source')}
if r['role'] == 'builder':
    # First candidate is deliberately wrong; actual test failure drives repair.
    a['edits'] = {'calc.py': 'def add(a, b):\n    return a ' + ('+' if r['last_checks'] else '-') + ' b\n'}
    a['proposal'] = 'Implement addition; acceptance remains operator-owned.'
else:
    a.update(verdict='accept', findings=[], addressed=r['findings'])
print(json.dumps(a))
