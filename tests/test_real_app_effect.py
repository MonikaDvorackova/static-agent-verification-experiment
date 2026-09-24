import importlib.util
import os
from pathlib import Path
import unittest


@unittest.skipUnless(os.environ.get('COPANE_CHECKOUT') and
                     importlib.util.find_spec('agents'),
                     'requires pinned COPANE_CHECKOUT and openai-agents SDK')
class CopaneEffectTests(unittest.IsolatedAsyncioTestCase):
    async def test_shell_write_bypasses_dedicated_tool_gate(self):
        from benchmark.real_world.copane_approval_path import probe
        self.assertEqual(await probe(Path(os.environ['COPANE_CHECKOUT'])),
                         (True, True, True))
