"""Offline, isolated probe of pinned Copane tool approval and shell write path.

Usage: python -m benchmark.real_world.copane_approval_path /path/to/copane
Requires openai-agents==0.22.3; never launches the full application or model API.
"""
from __future__ import annotations

import ast
import asyncio
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from typing import Any


COMMIT = 'e8392bb0730dee2f688acccff24fa0ba8f3ede29'
HASHES = {
    'run_command.py': '3c6f16e7fe6c5337452391e8cff75799c79930df8f6960a8f0456f6ad6b0525b',
    'write_file.py': 'b2a49bd64d18fadaa49bb27f977dc73798e6fe4c82014702e2d9392c1c600900',
    'tmux_agent.py': 'b38fdaa6ac5781d62b6a04bb9d4248c8cc54a72d504b4157df70dbfd9250bf1a',
}


def check_checkout(root: Path) -> None:
    revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != COMMIT:
        raise ValueError(f'expected pinned Copane revision {COMMIT}, got {revision}')
    base = root / 'python/src/copane'
    for name, digest in HASHES.items():
        path = base / ('tools' if name != 'tmux_agent.py' else '') / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'unexpected source content: {path}')
    tree = ast.parse((base / 'tmux_agent.py').read_text())
    registrations = [node.value for node in ast.walk(tree)
                     if isinstance(node, ast.AnnAssign) and
                     isinstance(node.target, ast.Attribute) and
                     node.target.attr == 'tools' and isinstance(node.value, ast.List)]
    if not any({'write_file', 'run_command'} <= {item.id for item in literal.elts
                if isinstance(item, ast.Name)} for literal in registrations):
        raise AssertionError('agent tool registration changed')


async def probe(root: Path) -> tuple[bool, bool, bool]:
    check_checkout(root)
    sys.path.insert(0, str(root / 'python/src'))
    from agents import Agent, ModelResponse, Runner, Usage, set_tracing_disabled
    from agents.models.interface import Model
    from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText
    from copane.tools import run_command, write_file

    set_tracing_disabled(True)
    if run_command.needs_approval is not False or write_file.needs_approval is not True:
        raise AssertionError('pinned tool approval declarations changed')

    class Script(Model):
        def __init__(self, tool: str, arguments: dict[str, Any]):
            self.tool, self.arguments, self.calls = tool, arguments, 0

        async def get_response(self, *args: Any, **kwargs: Any) -> ModelResponse:
            self.calls += 1
            if self.calls == 1:
                output = [ResponseFunctionToolCall(type='function_call',
                          name=self.tool, call_id='call-1', arguments=json.dumps(self.arguments))]
            else:
                output = [ResponseOutputMessage(id='done', type='message', role='assistant',
                          status='completed', content=[ResponseOutputText(type='output_text',
                          text='done', annotations=[])])]
            return ModelResponse(output=output, usage=Usage(), response_id=f'response-{self.calls}')

        async def stream_response(self, *args: Any, **kwargs: Any):
            raise AssertionError('unexpected streaming request')
            yield

    with tempfile.TemporaryDirectory(prefix='copane-p3-') as folder:
        shell_path = Path(folder) / 'shell.txt'
        write_path = Path(folder) / 'tool.txt'
        command = f"printf 'audit-only' > {shlex.quote(str(shell_path))}"
        agent = Agent(name='offline', instructions='offline', model=Script('run_command', {'cmd': command}),
                      tools=[run_command, write_file])
        shell_result = await Runner.run(agent, 'write temporary test file')
        shell_wrote_without_interrupt = not shell_result.interruptions and shell_path.read_text() == 'audit-only'
        guarded = Agent(name='offline', instructions='offline', model=Script('write_file',
                        {'path': str(write_path), 'content': 'audit-only'}),
                        tools=[run_command, write_file])
        guarded_result = await Runner.run(guarded, 'write temporary test file')
        write_paused = len(guarded_result.interruptions) == 1 and not write_path.exists()
        return shell_wrote_without_interrupt, write_paused, not write_path.exists()


if __name__ == '__main__':
    result = asyncio.run(probe(Path(sys.argv[1]).resolve()))
    assert result == (True, True, True)
    print('shell write without approval, write_file paused, no guarded file:', result)
