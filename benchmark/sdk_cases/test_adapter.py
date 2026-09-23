import unittest
from pathlib import Path
from benchmark.sdk_cases.adapter import analyze_tool
from benchmark.sdk_cases.evaluate import evaluate


class AdapterTests(unittest.TestCase):
    def test_labeled_cases_and_determinism(self):
        result = evaluate()
        self.assertEqual(result['summary']['cases'], 20)
        self.assertEqual(result['summary']['adapted_mismatches'], 0)
        self.assertEqual(result, evaluate())

    def test_dynamic_tool_registration_stays_unknown(self):
        source = (Path(__file__).parent / 'cases' / 'safe_bound.py').read_text()
        modified = source.replace('tools=[action]', 'tools=discover_tools()')
        result = analyze_tool(modified, 'dynamic.py')
        self.assertTrue(all(r.status == 'UNKNOWN' for r in result))
        self.assertIn('dynamic tools list', result[0].reasons[0])

    def test_dynamic_sdk_approval_stays_unknown(self):
        source = (Path(__file__).parent / 'cases' / 'safe_bound.py').read_text()
        modified = source.replace('needs_approval=False', 'needs_approval=policy')
        result = analyze_tool(modified, 'dynamic.py')
        self.assertTrue(all(r.status == 'UNKNOWN' for r in result))


if __name__ == '__main__':
    unittest.main()
