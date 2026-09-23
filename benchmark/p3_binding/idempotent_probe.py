"""Offline SDK plus an application-owned, atomic in-memory effect ledger.

The ledger is an experiment only: cross-process guarantees require durable,
transactional effect-side enforcement and authenticated workflow identity.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from threading import Lock

from agents import Agent, Runner, RunContextWrapper, function_tool, set_tracing_disabled

from benchmark.p3_binding.sdk_probe import ScriptedModel


class EffectLedger:
    def __init__(self) -> None:
        self.lock = Lock()
        self.records: dict[tuple[str, str], tuple[str, str]] = {}
        self.effects: list[tuple[str, str, int]] = []

    def pay(self, workflow: str, call_id: str, recipient: str, amount: int) -> str:
        payload = json.dumps(['pay', recipient, amount], separators=(',', ':'))
        fingerprint = hashlib.sha256(payload.encode()).hexdigest()
        key = (workflow, call_id)
        with self.lock:
            previous = self.records.get(key)
            if previous is not None:
                if previous[0] != fingerprint:
                    raise ValueError('call ID reused with different action or arguments')
                return previous[1]
            self.effects.append((workflow, recipient, amount))
            response = 'simulated'
            self.records[key] = (fingerprint, response)
            return response


async def run() -> tuple[int, bool, int]:
    set_tracing_disabled(True)
    ledger = EffectLedger()
    workflow = 'host-assigned-workflow-1'

    @function_tool(needs_approval=True)
    def pay(ctx: RunContextWrapper[None], recipient: str, amount: int) -> str:
        """Record an offline simulated payment once for each tool call ID."""
        # The SDK tool context supplies the call ID; the host supplies workflow.
        return ledger.pay(workflow, ctx.tool_call_id, recipient, amount)

    agent = Agent(name='offline', instructions='offline',
                  model=ScriptedModel({'recipient': 'Alice', 'amount': 10}), tools=[pay])
    paused = await Runner.run(agent, 'invoke tool')
    assert len(paused.interruptions) == 1
    assert not ledger.effects
    state = paused.to_state()
    state.approve(paused.interruptions[0])
    snapshot = state.to_json()
    await Runner.run(agent, await state.from_json(agent, snapshot))
    await Runner.run(agent, await state.from_json(agent, snapshot))
    after_two_resumes = len(ledger.effects)
    try:
        ledger.pay(workflow, 'call-1', 'Mallory', 100)
    except ValueError:
        mismatch_rejected = True
    else:
        mismatch_rejected = False
    # Calling effect storage directly bypasses SDK approval: complete mediation
    # remains a separate, mandatory premise.
    ledger.pay(workflow, 'direct-call', 'Mallory', 100)
    return after_two_resumes, mismatch_rejected, len(ledger.effects)


if __name__ == '__main__':
    result = asyncio.run(run())
    assert result == (1, True, 2)
    print('effects after two restores, mismatch rejected, after direct bypass:', result)
