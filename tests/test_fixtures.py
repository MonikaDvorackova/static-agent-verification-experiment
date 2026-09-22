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

if __name__ == '__main__':
    unittest.main()
