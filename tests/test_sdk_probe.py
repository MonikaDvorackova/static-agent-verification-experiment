import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec('agents'), 'openai-agents SDK not installed')
class OfflineSDKProbeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from agents import set_tracing_disabled
        set_tracing_disabled(True)

    async def test_paused_decision_and_snapshot_replay(self):
        from benchmark.p3_binding.sdk_probe import run_case, replay_case, altered_snapshot_case
        self.assertEqual(await run_case(False), (0, 0, []))
        self.assertEqual(await run_case(True),
                         (0, 1, [{'recipient': 'Alice', 'amount': 10}]))
        self.assertEqual(await replay_case(),
                         (2, [{'recipient': 'Alice', 'amount': 10}] * 2))
        self.assertEqual(await altered_snapshot_case(),
                         ([{'recipient': 'Alice', 'amount': 10}], 'resumed'))

    async def test_app_ledger_prevents_duplicate_resumes_but_allows_direct_bypass(self):
        from benchmark.p3_binding.idempotent_probe import run
        self.assertEqual(await run(), (1, True, 2))
