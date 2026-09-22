# Pysa baseline, 22 September 2026

This is a controlled overlap check, not a performance benchmark or a formal comparison of soundness. We installed `pyre-check==0.10.0` and Pyrefly in an isolated virtual environment; the repo contains only the source, source/sink rules and model declarations needed to reproduce the run, not installed binaries.

From `benchmark/pysa` run `pyre analyze` in an environment containing Pyre/Pysa and Pyrefly. The fixtures are five tiny functions using stubbed, modeled capabilities. Rule 6101 models P1 as `LLMOutput -> Privileged`, with `validate` modeled as a sanitizer for LLM taint. Rule 6102 models P2 as `Sensitive -> ExternalModel`. An authorization boundary is deliberately **not** modeled in these Pysa rules; P3 cannot be compared in this run.

| Function | Expected P1/P2 flow | Pysa 0.10.0 issue |
|---|---|---|
| `direct` | P1 | 6101 |
| `validated` | none | none |
| `nested` | none | none |
| `sensitive` | P2 | 6102 |
| `authorized_unvalidated` | P1 | 6101 |

Observed: three issues, precisely in the three expected functions. No unexpected issue on the remaining two. The configuration and stubs are in `benchmark/pysa/`. This is evidence that configurable static taint analysis covers the elementary P1/P2 examples already; it does not establish Pysa's results as proofs of safety, and it does not compare production code, precision, false negatives, or P3. See [official Pysa model documentation](https://pyre-check.org/docs/pysa-basics/) and [running guide](https://pyre-check.org/docs/pysa-running/).
