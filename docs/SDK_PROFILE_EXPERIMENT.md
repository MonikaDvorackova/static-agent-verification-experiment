# One-framework coverage experiment (23 September 2026)

## Question and setup

Can a narrowly specified OpenAI Agents SDK function-tool profile turn UNKNOWN into useful conditional decisions without silently treating SDK tool-call approval as permission for nested critical actions?

The corpus under `benchmark/sdk_cases/cases/` contains **20 authored SDK-shaped programs**, not unmodified programs from the SDK repository. Each has one `@function_tool(needs_approval=...)` and one `Agent(..., tools=[action])`. The 60 hand-specified property labels in `labels.tsv` assume immutable trusted contracts for the named source, sink and boundary functions; these labels are an **internal modeled reference**, not independently established runtime security ground truth. The generator and labels are in `build_cases.py`. No program or SDK dependency is executed.

The adapter recognizes precisely one unaliased SDK import, a single synchronous decorated tool with literal boolean approval configuration and inert `str` annotations, and a static one-tool registration. It uses Python AST, checks the shape and evaluates the tool body with the existing analyzer; rejected shapes return UNKNOWN with a reason. Its *additional assumptions* are that SDK and named capability implementations are sealed, that the chosen tool is callable, and that its body is the relevant entry. The adapter does not prove those assumptions in Python. It does not grant P3 approval when `needs_approval=True`: that flag gates the **SDK tool invocation** and cannot authorize a distinct `payment.execute(...)` inside the tool.

## Results

Run `python benchmark/sdk_cases/build_cases.py`, `python -m benchmark.sdk_cases.evaluate`, and `python -m unittest discover -s benchmark/sdk_cases -p 'test_*.py' -v` at the repository root. `results.json` contains every decision and diagnostic.

| On 20 cases / 60 property decisions | PROVED | VIOLATED | UNKNOWN | Incorrect PROVED against authored labels |
|---|---:|---:|---:|---:|
| Authored closed-world labels | 27 | 15 | 18 | — |
| Original analyzer, unchanged | 0 | 0 | 60 | 0 |
| Narrow experimental SDK adapter | 27 | 15 | 18 | 0 |

The adapter exactly matches labels on this **purpose-built** corpus, which is no estimate of real-world precision or soundness. Original UNKNOWN rate is 100%; adapter UNKNOWN rate is 30%. The number of incorrect PROVED is zero against the *authored* labels only. No independently labeled SDK repository or application has been evaluated with the adapter. The previously tested three unmodified agent-framework examples returned 9/9 UNKNOWN; those experiments were different programs and are not part of this table.

The SDK adapter itself requires a new module, rigid program-shape checks, tests and explicit assumptions merely to handle one static tool form. Dynamic registration and callable approval policies are rejected (tested). Effects within SDK internals, tool-to-tool calls, data schema coercion, tool output guardrails, async tools and mutable payloads remain unproved. A tool marked `needs_approval=True` that invokes `payment.execute(llm(request))` still violates modeled P1 and P3. This distinction is the most useful finding of this corpus.

## Pysa baseline on the same scenarios

Pysa 0.9.25 was run on type-only stand-ins for the same 20 tool bodies. `pysa/build_project.py` copies each body and injects imports of the modeled capabilities; `pysa/project/agents.py` is an inert approximation of the SDK decorator. This is **instrumented synthetic code**, not a run on the installed Agents SDK. The model uses the same three elementary rules from `BASELINE_COMPARISON.md`: LLM-origin taint to privileged sink, sensitive taint to external sink, and a weaker P3 approximation (unapproved LLM-origin taint to critical sink, with approval as sanitizer). No model validation errors were returned.

| Pysa property alert | Known VIOLATED cases detected | Known violations missed | Alerts on UNKNOWN labels |
|---|---:|---|---:|
| P1 | 4/4 | none | 2 |
| P2 | 3/3 | none | 0 |
| P3 | 4/8 | `constant_payment`, `sensitive_tool`, `unrelated_approval`, `wrong_action` | 1 |

Pysa emitted 14 alerts in total (11 on labeled violations, three on deliberately UNKNOWN cells). An alert in an UNKNOWN cell is **not** evidence of a false alarm; ground truth is unresolved there. Likewise, no alert is **not** PROVED. P3 misses are limitations of this particular taint configuration, not Pysa generally. The absence of modeled argument-bound approval in its sanitizer explains the wrong-action miss; a constant payment has no taint source. The harness and raw issue JSON are in `pysa/`.

Reproduce with `python benchmark/sdk_cases/pysa/build_project.py`, create a virtual environment with `pyre-check==0.9.25`, and run `pyre analyze --output-format=json > results.json` from `benchmark/sdk_cases/pysa/`, then `python benchmark/sdk_cases/pysa/score.py` from the repository root. Keep Pysa output separate from the SDK adapter's three-valued statuses.

**CodeQL was not run on this 20-case corpus.** A later narrow CodeQL query was executed on the pinned external OpenKB source (`REAL_WORLD_CODEQL_EXPERIMENT.md`); it is a separate path observation, not a comparable 20-case baseline or CodeQL accuracy estimate. Independent annotation across real agent repositories and framework model effort remain open. Do not interpret this benchmark as evidence for a new language.

Sources for SDK behavior: [function tool API](https://openai.github.io/openai-agents-python/ref/tool/) and [tool approval documentation](https://openai.github.io/openai-agents-python/tools/). Existing analysis approaches: [Pysa basics](https://pyre-check.org/docs/pysa-basics/), [CodeQL Python data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/).
