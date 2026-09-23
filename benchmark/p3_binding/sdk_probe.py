"""Offline OpenAI Agents SDK approval probe; no model/API/network call or real payment.

Run with openai-agents==0.22.3: python -m benchmark.p3_binding.sdk_probe
"""
from __future__ import annotations

import asyncio
import copy
import json
from typing import Any

from agents import Agent, ModelResponse, Runner, Usage, function_tool, set_tracing_disabled
from agents.models.interface import Model
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText


class ScriptedModel(Model):
    def __init__(self, args: dict[str, Any]):
        self.args = args
        self.calls = 0

    async def get_response(self, *args: Any, **kwargs: Any) -> ModelResponse:
        self.calls += 1
        if self.calls == 1:
            output = [ResponseFunctionToolCall(type='function_call', name='pay',
                        call_id='call-1', arguments=json.dumps(self.args))]
        else:
            output = [ResponseOutputMessage(id='message-2', type='message', role='assistant', status='completed',
                        content=[ResponseOutputText(type='output_text', text='done', annotations=[])])]
        return ModelResponse(output=output, usage=Usage(), response_id=f'response-{self.calls}')

    async def stream_response(self, *args: Any, **kwargs: Any):
        raise AssertionError('streaming not part of this experiment')
        yield


async def run_case(approve: bool) -> tuple[int, int, list[dict[str, Any]]]:
    effects: list[dict[str, Any]] = []

    @function_tool(needs_approval=True)
    def pay(recipient: str, amount: int) -> str:
        """Record a simulated payment with the named recipient and amount."""
        effects.append({'recipient': recipient, 'amount': amount})
        return 'simulated'

    agent = Agent(name='offline', instructions='offline', model=ScriptedModel(
        {'recipient': 'Alice', 'amount': 10}), tools=[pay])
    paused = await Runner.run(agent, 'invoke the tool')
    before = len(effects)
    assert len(paused.interruptions) == 1
    pending = paused.interruptions[0]
    assert json.loads(pending.arguments) == {'recipient': 'Alice', 'amount': 10}
    state = paused.to_state()
    if approve:
        state.approve(pending)
    else:
        state.reject(pending)
    await Runner.run(agent, state)
    return before, len(effects), effects


async def replay_case() -> tuple[int, list[dict[str, Any]]]:
    """Restore an approved snapshot twice as two independent resume lineages."""
    effects: list[dict[str, Any]] = []

    @function_tool(needs_approval=True)
    def pay(recipient: str, amount: int) -> str:
        """Record an offline simulated payment."""
        effects.append({'recipient': recipient, 'amount': amount})
        return 'simulated'

    agent = Agent(name='offline', instructions='offline',
                  model=ScriptedModel({'recipient': 'Alice', 'amount': 10}), tools=[pay])
    paused = await Runner.run(agent, 'invoke the tool')
    state = paused.to_state()
    state.approve(paused.interruptions[0])
    snapshot = state.to_json()
    await Runner.run(agent, await state.from_json(agent, snapshot))
    await Runner.run(agent, await state.from_json(agent, snapshot))
    return len(effects), effects


async def altered_snapshot_case() -> tuple[list[dict[str, Any]], str]:
    """Try changing one serialized call argument after approval (untrusted storage)."""
    effects: list[dict[str, Any]] = []

    @function_tool(needs_approval=True)
    def pay(recipient: str, amount: int) -> str:
        """Record an offline simulated payment."""
        effects.append({'recipient': recipient, 'amount': amount})
        return 'simulated'

    agent = Agent(name='offline', instructions='offline',
                  model=ScriptedModel({'recipient': 'Alice', 'amount': 10}), tools=[pay])
    paused = await Runner.run(agent, 'invoke the tool')
    state = paused.to_state()
    state.approve(paused.interruptions[0])
    altered = copy.deepcopy(state.to_json())
    altered['model_responses'][0]['output'][0]['arguments'] = json.dumps(
        {'recipient': 'Mallory', 'amount': 100})
    try:
        await Runner.run(agent, await state.from_json(agent, altered))
    except Exception as exc:
        return effects, type(exc).__name__
    return effects, 'resumed'


async def main() -> None:
    set_tracing_disabled(True)
    rejected = await run_case(False)
    approved = await run_case(True)
    assert rejected == (0, 0, [])
    assert approved == (0, 1, [{'recipient': 'Alice', 'amount': 10}])
    print('rejected:', rejected)
    print('approved:', approved)
    replay = await replay_case()
    assert replay == (2, [{'recipient': 'Alice', 'amount': 10}] * 2)
    print('two restores of same approved snapshot:', replay)
    altered = await altered_snapshot_case()
    print('changed one serialized argument field:', altered)


if __name__ == '__main__':
    asyncio.run(main())
