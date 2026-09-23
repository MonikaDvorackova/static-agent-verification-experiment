# Static Agent Verification Experiment

Experimental research prototype, **not a production security product**. Independent of AIGov. It parses a small Python subset with `ast`, lowers statements into a location/effect-bearing IR, explores branches and local function calls, and checks P1 unvalidated LLM data at privileged sinks, P2 sensitive data at unauthorized external sinks, and P3 actions without a payload-bound authorization boundary. It never invokes an LLM or analyzed code.

```bash
python -m src tests/unsafe/direct.py
python -m unittest discover -s tests -v
```

The deliberately narrow API model recognizes `llm`, `external_read`, `user_input`, `sensitive_data`, `validate`, `sanitize`, `authorize`, `human_approve`, `authorize_action`, `human_approve_action`, `external_llm`, `external_tool`, `fs.write`, `db.mutate`, and `payment.execute`. A label `PROVED` only describes paths in the modeled subset **assuming these names resolve to sealed, audited contracts**. Ordinary Python does not seal names; do not use these results to authorize real operations. Unknown dynamic behavior produces a location and reason. The current engine is a path-sensitive interpreter over AST-backed IR, not a general CFG construction, SSA compiler, or whole-program proof system.

## Layout

- `docs/THREAT_MODEL.md`, `FORMAL_MODEL.md`: scope, P1–P3 and result semantics.
- `docs/PYTHON_LIMITATIONS.md`, `LANGUAGE_JUSTIFICATION.md`, `RELATED_WORK.md`: limitations and research conclusion.
- `src/parser/`: AST parsing and instruction extraction.
- `src/ir/`: abstract values and state.
- `src/analysis/`: path traversal, calls, labels and decisions.
- `src/policies/`: modeled API contracts.
- `src/diagnostics/`: result records.
- `tests/safe`, `tests/unsafe`, `tests/unknown`: twenty-eight documented adversarial fixtures; `tests/expectations.tsv` gives per-property outcomes.

An eight-function Pysa comparison with reproducible models is in `benchmark/pysa/` and `docs/BASELINE_COMPARISON.md`. It covers P1/P2 and a partial P3 approximation. Three unmodified public agent examples are analyzed in `docs/PUBLIC_CODE_EXPERIMENT.md` (all UNKNOWN). `docs/P3_COMPARISON.md` explains the static/runtime authorization boundary.

`benchmark/sdk_cases/` adds an authored 20-case OpenAI Agents SDK-shaped corpus with hand-specified closed-world labels, an experimental AST adapter for one static function-tool form, and a Pysa 0.9.25 comparison using instrumented type-only stubs. Results and the missing CodeQL baseline are explained in `docs/SDK_PROFILE_EXPERIMENT.md`. No real-world false-PROVED rate can be inferred from these authored cases.

`docs/REAL_WORLD_CODEQL_EXPERIMENT.md` reports a separately pinned OpenKB source inspection and an actually executed narrow CodeQL query for one agent-tool-to-file-write flow. The external code is not bundled. Both variants of our analyzer return UNKNOWN on the unchanged project; the CodeQL result is a possible flow warning, not a security verdict.

`docs/MULTI_PROJECT_BENCHMARK.md` extends the selected-path evaluation to three pinned public agent projects. Our analyzer and SDK adapter return UNKNOWN on all three unchanged modules; narrow CodeQL queries find two direct file-write flows and one scheduling edge. The manual labels are conditional and not independent ground truth; no production safety claim or real-world Pysa accuracy estimate follows.

For a stronger *modeled* P3 contract, `human_approve_action('payment.execute', validated_value)` binds the approval value to a literal sink name. Using it at another sink produces `VIOLATED`; a computed target produces `UNKNOWN`. This only works under the sealed-contract assumption and does not verify that a human saw the concrete arguments.

## Important qualifications

Nonconstant branch tests are UNKNOWN because Python truth testing can execute code and may reveal information through control flow; constant branches are followed precisely. Exception handling is UNKNOWN. Arbitrary imports, decorators, globals, reflection, mutation, callbacks, dynamic calls, Python descriptors, async and loops are not analyzed soundly. The IR records effects, but no complete effect inference or separate graph algorithm exists yet. A named `validate`/`human_approve` is a stipulated trusted primitive, not verified Python code. Results are research hypotheses conditional on a sealed environment. The comparison in `docs/RELATED_WORK.md` finds no demonstrated need yet for a new language; the present baseline is too small to support performance or whole-program claims.
