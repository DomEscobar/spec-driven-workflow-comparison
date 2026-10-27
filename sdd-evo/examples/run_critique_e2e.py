#!/usr/bin/env python3
"""Real Git/CLI repair flow; scripted critic fixture, not independent review."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_critique import CritiqueTests

if __name__ == '__main__':
    print('Real temporary Git repo + actual tests/probe. Critic and manual review are SCRIPTED protocol fixtures.', flush=True)
    suite = unittest.TestSuite([CritiqueTests('test_real_repair_e2e')])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print('Verified: latent negative-number defect -> import -> actual repair/check -> dispositions -> manual-review gate -> local finish -> stale rejection -> repair-budget rejection.')
    sys.exit(0 if result.wasSuccessful() else 1)
