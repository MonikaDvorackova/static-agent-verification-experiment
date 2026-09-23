# Pinned external-code experiment: OpenKB

## Scope and independent annotation

On 23 September 2026, we inspected [VectifyAI/OpenKB](https://github.com/VectifyAI/OpenKB/tree/ff54396e575ee6feb0113b631a34caa082b441cc) at commit `ff54396e575ee6feb0113b631a34caa082b441cc`. Its `openkb/agent/query.py` registers an OpenAI Agents SDK `@function_tool` named `write_file` in `build_chat_agent`; `openkb/agent/tools.py` implements `write_kb_file`, which limits paths to `wiki/explorations/**` and `output/**` before invoking `atomic_write_text` in `openkb/locks.py`. This is an **intended, path-confined file-writing tool**. The project source was cloned to a temporary checkout, inspected and parsed; no agent code, model call or write tool was executed. Its source is not copied into this repository.

The manually annotated selected path is `write_file(content)` (query.py:237) → `write_kb_file(path, content, kb_root)` (query.py:251) → `atomic_write_text(full_path, content)` (tools.py:255). The labels in `benchmark/real_world/openkb-annotations.tsv` were written from source inspection **before the CodeQL run**:

| Property | Selected path assessment | Reason |
|---|---|---|
| P1 | **VIOLATED, conditional model** | If SDK tool arguments are untrusted LLM-origin values and a file write counts as privileged, `content` reaches the file-write helper without a modeled semantic validation boundary. Path confinement checks the destination, not the content. This is a possible-flow finding, not a finding of exploitation. |
| P2 | **UNKNOWN** | The confidentiality of wiki content and external-model recipient authorization cannot be established from this selected path. |
| P3 | **UNKNOWN** | A path allow-list is an explicit restriction of destination authority. Whether the chosen P3 policy additionally requires human approval for each allowed write is unspecified; the tool registration itself does not present a literal SDK approval flag. No assertion that the application violates its intended authorization policy is justified. |

Other read tools and dynamic skill registration make whole-application judgments still more uncertain. There is one selected write path, not an independently labeled application-level test suite. The annotation is conditional on a documented source/sink interpretation and is not runtime ground truth.

## Unmodified-source results

`benchmark/real_world/run_openkb.py` verifies the clean checkout revision and analyzes the **unaltered** `query.py`, `tools.py`, and `locks.py`. SHA-256 fingerprints and explanations are in `benchmark/real_world/openkb-results.json`. For each of three files and three properties, both the original analyzer and the 20-case SDK adapter returned **UNKNOWN (9/9 each)**. The original requires a recognized `@agent` entry; the adapter accepts exactly one statically registered top-level synchronous tool, whereas OpenKB has imports, nested tools, an asynchronous runner and a dynamic tool list. Thus zero false PROVED are observed only because neither analyzer makes a proof; no real-world false-PROVED rate follows.

A specialized CodeQL query, `benchmark/real_world/codeql/ToolArgumentToKbWrite.ql`, was **compiled and executed** over a database extracted from the pinned, unmodified OpenKB checkout. CodeQL CLI `2.27.1`, library revision `03cccfe9a77c67c349d1ec557c9959b0ab5cd739`, and the checked release bundle were used. `benchmark/real_world/codeql-summary.json` records **one** result: `query.py:237` `content` may flow to the `write_kb_file` call argument at `query.py:251`. The query explicitly names this function and file. It does not verify the downstream `atomic_write_text` call, whether a runtime path is permitted, the truth of the SDK source assumption, validation correctness, P2 or P3. A CodeQL finding is a possible-flow warning, **not** `VIOLATED` or `PROVED` in our three-valued semantics.

## Reproduction and limits

1. Obtain a clean OpenKB checkout pinned to `ff54396e575ee6feb0113b631a34caa082b441cc`. From this repository root, run `python -m benchmark.real_world.run_openkb /path/to/OpenKB` and compare the generated output to `benchmark/real_world/openkb-results.json`.
2. Obtain CodeQL CLI `2.27.1` plus the CodeQL Python query libraries from the pinned [`github/codeql`](https://github.com/github/codeql/tree/03cccfe9a77c67c349d1ec557c9959b0ab5cd739) revision. Create a database with `codeql database create /tmp/openkb-db --language=python --source-root=/path/to/OpenKB`. Run `codeql database analyze /tmp/openkb-db benchmark/real_world/codeql/ToolArgumentToKbWrite.ql --format=sarif-latest --output=/tmp/openkb.sarif --search-path=/path/to/codeql-libraries`; inspect the one query result and its related source location. No key, dependency installation or runtime execution of OpenKB is needed.
3. The concrete released CLI bundle was `codeql.zip` from [v2.27.1](https://github.com/github/codeql-cli-binaries/releases/tag/v2.27.1), SHA-256 `382b9c3b8c4d91f6413170d325fa5ac6c45e8906b64d3a0f884811f3931b6e2c`. The CodeQL library source was cloned separately; these exact versions are part of the experiment.

This compares a narrow CodeQL flow warning with the analyzer's explicit UNKNOWN, not equivalent whole-program judgments. P2 and P3 still lack comparable CodeQL queries. A broader evaluation requires independent labels across multiple external applications, source/sink contract review and measurements of model-authoring effort. No evidence here justifies inventing a new language.
