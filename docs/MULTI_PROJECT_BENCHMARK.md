# Three public agent applications: selected write paths

This is a small follow-up to `REAL_WORLD_CODEQL_EXPERIMENT.md`, undertaken on 23 September 2026. It measures whether the prototype can decide P1–P3 on **unchanged** Python modules from three public agent applications, and whether a configured CodeQL query can confirm the selected data path. It is not a random or representative sample, and the analyst who wrote the CodeQL queries also selected and annotated the paths. Thus annotations are human reviewed, **not blind or independent ground truth**. Agent code was read and parsed; no agent or model was executed.

| Public project / pinned revision | Selected tool and registration | Relevant effect |
|---|---|---|
| [VectifyAI/OpenKB](https://github.com/VectifyAI/OpenKB/tree/ff54396e575ee6feb0113b631a34caa082b441cc), `ff54396e...` | `openkb/agent/query.py` nested `@function_tool write_file` added via `base.clone(tools=[*base.tools, *extra_tools])` | Allowed paths under `wiki/explorations/**` and `output/**` reach `atomic_write_text` |
| [MostafaKashwaa/copane](https://github.com/MostafaKashwaa/copane/tree/e8392bb0730dee2f688acccff24fa0ba8f3ede29), `e8392bb...` | `python/src/copane/tools/write_file.py` async tool with `@function_tool(needs_approval=True)` and another `@traceable` decorator, registered from `tmux_agent.py` | `f.write(content)`; SDK tool approval is declared but runtime boundary and additional decorator are not statically verified |
| [Kkooops/OpenAI-Based-Agent](https://github.com/Kkooops/OpenAI-Based-Agent/tree/9bbf71fc70dd266e1d67e5be697eea2e84b4cdf2), `9bbf71fc...` | `src/tools/write_file_tool.py` async `@function_tool` registered from `src/cli.py` | Workspace-limited path is sent to `_write_file` through `asyncio.to_thread`; helper calls `fh.write(content)` |

`benchmark/real_world/corpus-annotations.tsv` records the narrow manual assessment. For all three paths **P1 is a conditional modeled counterexample only if** SDK tool arguments are untrusted LLM output and file writes are privileged. The study does not establish that an adversarial model has actually generated a harmful string or that a restricted destination check fails. **P2 remains UNKNOWN**: sensitivity and recipient authority are not classified. **P3 remains UNKNOWN**: OpenKB and the third project constrain destinations; Copane declares an SDK approval gate, but its implementation, extra decorator, possible bypass routes and intended action policy were not proved by our analyzer. A missing literal approval flag alone is not a verified P3 violation.

## Observations

| Observation on selected modules | OpenKB | Copane | OpenAI-Based-Agent |
|---|---:|---:|---:|
| Original analyzer P1/P2/P3 | 3 UNKNOWN | 3 UNKNOWN | 3 UNKNOWN |
| Experimental SDK adapter P1/P2/P3 | 3 UNKNOWN | 3 UNKNOWN | 3 UNKNOWN |
| CodeQL named write query: possible content-flow results | 2 (helper call and underlying `fh.write`) | 1 (`f.write`) | 0 |
| CodeQL `to_thread` scheduling-edge query | not run | not run | 1 (tool content → scheduled helper argument) |

The direct CodeQL query, `ToolContentToFileWrite.ql`, matches a `write_file` parameter named `content` in three **manually selected files** and sinks matching `.write(content)` or `write_kb_file(..., content, ...)`. Its two OpenKB results include the underlying byte write in `locks.py:232` and the wrapper in `query.py:251`. Copane yields one result at `write_file.py:41`. In the third project, this query reports **zero**, because the flow crosses `asyncio.to_thread`. The separate `ToolContentToThreadedWrite.ql` reports one edge to the scheduling call at `write_file_tool.py:72`; manual inspection of `_write_file` supplies the remainder. That edge is not an end-to-end CodeQL proof of the write. These are possible-flow findings, not security verdicts, not `PROVED` results, and not a CodeQL measurement of P2 or P3.

`benchmark/real_world/corpus-results.json` records clean-checkout revision checks, content hashes and every analyzer diagnostic. `benchmark/real_world/corpus-codeql-summary.json` records the CodeQL result locations. No external source code or CodeQL binaries are committed. CLI version was `2.27.1`; pinned CodeQL library revision was `03cccfe9a77c67c349d1ec557c9959b0ab5cd739`. Reproduce by cloning each linked project at the exact commit, running:

```bash
python -m benchmark.real_world.run_corpus /path/to/OpenKB /path/to/copane /path/to/OpenAI-Based-Agent
codeql database create /tmp/target-db --language=python --source-root=/path/to/target
codeql database analyze /tmp/target-db benchmark/real_world/codeql/ToolContentToFileWrite.ql --format=sarif-latest --output=/tmp/target.sarif --search-path=/path/to/pinned-codeql-libraries
```

For the third project's scheduling edge, run `ToolContentToThreadedWrite.ql` against its database with the same command. If CLI/library versions change, results must be regenerated. The earlier **Pysa** baseline was run on 20 authored SDK-shaped cases using explicit type-only stubs; it was **not** run on these three unchanged projects with equivalent contracts, so no Pysa-vs-CodeQL real-world accuracy rate is claimed. Building trustworthy Pysa models for the same three sources and finding external reviewers for the labels remain open.

## Research decision

The current Python AST prototype makes **zero** property decisions on these three selected real modules. Specialized CodeQL queries establish two real direct flows and one scheduled-helper edge. This supports prioritizing framework models and comparison with existing analysis tools over adding another ad hoc rule or new language syntax. It does **not** show that CodeQL can prove P1–P3 for arbitrary agent applications, nor that a new language is needed. A future larger evaluation should require independently reviewed path labels and count wrong `PROVED` results only when the target property and trusted contracts are specified in advance.

A later, separately scoped experiment in `REAL_APP_EFFECT_MEDIATION.md` runs two of Copane's pinned tools offline. It demonstrates a concrete shell-based write without an approval interruption under an **analyst-defined** all-agent-file-writes policy. It does not change this benchmark's whole-module UNKNOWN verdict or establish the project's intended global P3 policy.
