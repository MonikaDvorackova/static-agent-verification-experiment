# Pysa baseline, 22 September 2026

This is a controlled overlap check, not a performance benchmark or a formal comparison of soundness. We installed `pyre-check==0.10.0` and Pyrefly in an isolated virtual environment. The repo contains the source, rules and model declarations, but no installed binaries. From `benchmark/pysa`, run `pyre analyze` with both tools available.

Rule 6101 models P1 as `LLMOutput -> Privileged` with `validate` as an LLM-taint sanitizer. Rule 6102 models P2 as `Sensitive -> ExternalModel`. Rule 6103 approximates P3 as `Unapproved -> Critical` with `human_approve` as an `Unapproved` sanitizer. These are developer-supplied contracts, not verified implementations. The functions are synthetic stubs to keep the comparison controlled.

| Function | Pysa issues | P3 expectation in the stronger action-bound sense |
|---|---|---|
| `direct` | P1, P3 | Missing approval detected |
| `validated` | P3 | Missing approval detected |
| `nested` | none | Approval flow accepted |
| `sensitive` | P2 | No critical action |
| `authorized_unvalidated` | P1 | Approval flow accepted; P1 still fails |
| `approved_other_payload` | P1, P3 | Approval of unrelated value does not pass |
| `constant_action` | none | **P3 false negative:** action argument has no `Unapproved` source |
| `modified_after_approval` | P1 | **P3 false negative:** sanitizer erases the label before the argument is modified |

Observed: eight Pysa issues across eight functions, with zero model-verification errors; P3 rule found three of five intended unauthorized-action examples and missed the two specified above. This is a limitation of **these models**, not proof that Pysa or CodeQL cannot encode richer stateful rules. An occurrence query for critical calls would catch the constant case but would need a flow/path rule to recognize valid authorization. A capability/effect system could restrict critical actions to code holding a checked authority token. Even then, a trusted implementation must bind the approval to the exact target, arguments, identity and time, and the execution path must prevent bypass.

These results do not establish that our prototype is more sound than Pysa. Our own `PROVED` results remain conditional on sealed contracts, which ordinary Python does not enforce. See [Pysa models](https://pyre-check.org/docs/pysa-basics/), [CodeQL Python data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/), and [static tracked capabilities for agents](https://arxiv.org/abs/2603.00991).
