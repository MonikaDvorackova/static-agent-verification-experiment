import csv
import unittest
from pathlib import Path
from src.analysis.engine import analyze

ROOT = Path(__file__).parent

class FixtureTests(unittest.TestCase):
    def test_expectations(self):
        with (ROOT / 'expectations.tsv').open() as f:
            for row in csv.DictReader(f, delimiter='\t'):
                with self.subTest(row['fixture']):
                    path = ROOT / row['fixture']
                    results = analyze(path.read_text(), str(path))
                    self.assertEqual(tuple(r.status for r in results),
                                     (row['P1'], row['P2'], row['P3']))
                    for result in results:
                        if result.status != 'PROVED':
                            self.assertTrue(result.reasons)

    def test_unknown_reasons_and_determinism(self):
        for fixture, fragment in (
            ('unknown/implicit_flow.py', 'dynamic truthiness'),
            ('unknown/approval_reuse.py', 'authorization result reused'),
            ('unknown/function_default.py', 'function default expression'),
            ('unknown/dynamic_approval_target.py', 'approval action must be a literal'),
        ):
            with self.subTest(fixture):
                source = (ROOT / fixture).read_text()
                first = analyze(source, fixture)
                self.assertEqual(first, analyze(source, fixture))
                self.assertTrue(any(fragment in reason for result in first for reason in result.reasons))

if __name__ == '__main__':
    unittest.main()
