# Real application: whether one file-write approval gate mediates every write

24 September 2026. Selected public application: [MostafaKashwaa/copane](https://github.com/MostafaKashwaa/copane/tree/e8392bb0730dee2f688acccff24fa0ba8f3ede29) at commit `e8392bb0730dee2f688acccff24fa0ba8f3ede29`. The narrow **research policy** is: *every agent-requested write to an arbitrary filesystem path must be approved before execution*. This is an analyst-defined P3* instance, **not** a statement of the project's declared global security policy or a finding about any production deployment. All tested writes went to a disposable local temporary directory.

## Source and effect inventory

The existing three-project comparison found an agent-supplied `content` flow through the `write_file` tool to `f.write(content)` with CodeQL. This follow-up examined the same pinned checkout's tool registration and adjacent effects. `TmuxAgent.__init__` registers `write_file`, `edit_file` **and** `run_command`. The first two use `@function_tool(needs_approval=True)`; the latter uses `@function_tool` with no approval flag and invokes `subprocess.run(cmd, shell=True)` after a finite denylist heuristic. That heuristic rejects selected destructive patterns but does not classify ordinary shell redirection as an approval-required file write. The trace decorator is conditional: its pass-through form was used in this offline probe. The LangSmith-enabled path was not tested.

There are additional application writes for session data, logs and configuration. This study does **not** classify all of them as agent-requested critical effects, audit every other import or external library, or assert whole-application complete mediation. It is enough to show two reachable routes to the same *class* of effect in the agent's registered tool set.

## Reproducible observation

`benchmark/real_world/copane_approval_path.py` requires a clean checkout at the pinned commit and checks the exact hashes of `run_command.py`, `write_file.py` and `tmux_agent.py`. It parses agent tool registration with `ast`, imports the actual pinned tools and runs them via OpenAI Agents SDK **0.22.3** with a deterministic scripted model. Copane declares `openai-agents>=0.13.5`; this is a test of its source with one allowed SDK version, not its full supported range. No live model, tmux UI or network service is invoked.

1. A tool call to `run_command` receives a benign `printf 'audit-only' > <temp>/shell.txt`. The SDK returns without a tool approval interruption and the temporary file contains `audit-only`.
2. A tool call to `write_file` targeting `<temp>/tool.txt` produces one SDK approval interruption; before approval, the file does not exist.

The probe returns `(True, True, True)`: shell write without approval, `write_file` paused, and no write from the paused tool. Reproduce with `pip install 'openai-agents==0.22.3' socksio`, clone the linked project at its pinned SHA, then `python -m benchmark.real_world.copane_approval_path /path/to/copane`. The harness deliberately never approves the guarded write. It does **not** run arbitrary model-generated commands, and the only shell command in the experiment writes fixed harmless text to its own temporary file.

| Requirement | Result | Reason |
|---|---|---|
| Analyst policy: every agent-requested arbitrary filesystem write is approved | **VIOLATED**, conditional on that policy | Registered shell tool performs one concrete write without an SDK approval interruption. |
| The application's actual intended global file-write policy | **UNKNOWN** | Tool descriptions require approval for `write_file`/`edit_file`, while `run_command` is expressly available for general commands; no explicit whole-application policy was established. |
| P3* for every critical external action in the application | **UNKNOWN** | Critical-action inventory, human identity, durable approval binding and all effect entry points were not established. |
| Static prototype on unchanged Copane module | **UNKNOWN** | Its previously reported result remains unchanged; this is a separate, policy-specific real SDK execution. |

## Consequence for the research question

Approval attached to individual tools does not establish complete effect mediation when another registered tool can implement the same effect. A static capability system can close this route only if it restricts **shell execution as an effect** or proves it cannot write arbitrary files, and if the trusted host denies other unrestricted effect APIs. A runtime mediator likewise needs an exhaustive effect inventory; checking a tool name is insufficient. This result does **not** identify a gap requiring a new language: existing language subsets and runtime restrictions can in principle require all writes and shell effects to cross audited capabilities, but this exact system was not retrofitted or formally proved.

**Stop/go decision:** do not expand the prototype or design syntax on the strength of this observation. For a claim stronger than this conditional counterexample, obtain an independently reviewed target policy and audit the full trusted effect boundary in one application. If ordinary existing tools can enforce it under workable constraints, the language proposal should stop.
