#!/usr/bin/env python3
"""Negative controls for the documentation checker, in temporary copies."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_docs', ROOT / 'scripts/check_docs.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CheckerTests(unittest.TestCase):
    def mutate(self, path, addition):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'repo'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            file = copy / path
            file.write_text(file.read_text() + addition)
            return checker.check(copy)[1]

    def test_clean(self):
        self.assertEqual(checker.check()[1], [])

    def test_missing_link(self):
        self.assertTrue(self.mutate('README.md', '\n[Broken](missing-file.md)\n'))

    def test_missing_anchor(self):
        self.assertTrue(self.mutate('README.md', '\n[Broken](sources.md#absent-anchor)\n'))

    def test_table_width(self):
        self.assertTrue(self.mutate('README.md', '\n| A | B |\n|---|---|\n| A |\n'))

    def test_placeholder_url(self):
        self.assertTrue(self.mutate('README.md', '\n[Bad](https://example.com/source)\n'))

    def test_unclosed_fence(self):
        self.assertTrue(self.mutate('README.md', '\n```text\nunfinished\n'))

    def test_invalid_json(self):
        self.assertTrue(self.mutate('README.md', '\n```json\n{bad}\n```\n'))

    def test_private_marker(self):
        self.assertTrue(self.mutate('README.md', '\n/root/private-location\n'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
