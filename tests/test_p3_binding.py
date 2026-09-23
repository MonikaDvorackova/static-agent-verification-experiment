import unittest

from benchmark.p3_binding.run import results


class P3BindingProbeTests(unittest.TestCase):
    def test_conditional_verdicts_and_strict_gap(self):
        self.assertEqual(results(), {
            'matching_literal': ('PROVED', 'UNKNOWN'),
            'wrong_action': ('VIOLATED', 'UNKNOWN'),
            'dynamic_action': ('UNKNOWN', 'UNKNOWN'),
            'reused_approval': ('UNKNOWN', 'UNKNOWN'),
            'alias_modified_after_approval': ('UNKNOWN', 'UNKNOWN'),
            'unmediated_effect': ('UNKNOWN', 'UNKNOWN'),
        })


if __name__ == '__main__':
    unittest.main()
