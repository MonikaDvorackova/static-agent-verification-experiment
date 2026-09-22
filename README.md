# Static Agent Verification Experiment

Experimental research prototype, **not a production security product**. Independent of AIGov. It parses a small Python subset with `ast`, lowers statements into a location/effect-bearing IR, explores branches and local function calls, and checks P1 unvalidated LLM data at privileged sinks, P2 sensitive data at unauthorized external sinks, and P3 actions without a payload-bound authorization boundary. It never invokes an LLM or analyzed code.

```bash
python -m src tests/unsafe/direct.py
python -m unittest discover -s tests -v
```

The deliberately narrow API model recognizes `llm`, `external_read`, `user_input`, `sensitive_data`, `validate`, `sanitize`, `authorize`, `human_approve`, `external_llm`, `external_tool`, `fs.write`, `db.mutate`, and `payment.execute`. A label `PROVED` only describes paths in the modeled subset **assuming these names resolve to sealed, audited contracts**. Ordinary Python does not seal names; do not use these results to authorize real operations. Unknown dynamic behavior produces a location and reason. The current engine is a path-sensitive interpreter over AST-backed IR, not a general CFG construction, SSA compiler, or whole-program proof system.

## Layout

- `docs/THREAT_MODEL.md`, `FORMAL_MODEL.md`: scope, P1–P3 and result semantics.
- `docs/PYTHON_LIMITATIONS.md`, `LANGUAGE_JUSTIFICATION.md`, `RELATED_WORK.md`: limitations and research conclusion.
- `src/parser/`: AST parsing and instruction extraction.
- `src/ir/`: abstract values and state.
- `src/analysis/`: path traversal, calls, labels and decisions.
- `src/policies/`: modeled API contracts.
- `src/diagnostics/`: result records.
- `tests/safe`, `tests/unsafe`, `tests/unknown`: sixteen documented adversarial fixtures; `tests/expectations.tsv` gives per-property outcomes.

A five-function Pysa comparison with reproducible models is in `benchmark/pysa/` and `docs/BASELINE_COMPARISON.md`. It shows that existing static taint analysis already captures the elementary P1/P2 cases. P3 was not benchmarked against Pysa.

## Important qualifications

Branches are conservatively both feasible; exception handling is UNKNOWN. Arbitrary imports, decorators, globals, reflection, mutation, callbacks, dynamic calls, Python descriptors, async and loops are not analyzed soundly. The IR records effects, but no complete effect inference or separate graph algorithm exists yet. A named `validate`/`human_approve` is a stipulated trusted primitive, not verified Python code. Results are research hypotheses conditional on a sealed environment. The comparison in `docs/RELATED_WORK.md` finds no demonstrated need yet for a new language; benchmark this subset against established tools before expanding it.
