# Existing-language capability and approval experiment

23 September 2026. This experiment compares two **existing mechanisms** for a narrow P3* question. Code is in `benchmark/p3_binding/scala/` and `benchmark/p3_binding/idempotent_probe.py`. It is independent of AIGov. None of the examples sends a payment, invokes a real model, or establishes a production security guarantee.

## Questions and observed results

| Question | Test | Observation | Bound |
|---|---|---|---|
| Can code request the modeled effect when given the typed capability? | `Allowed.scala` | Compiles with Scala 3.9.0 safe mode and capture checking. | The host must safely construct and restrict the capability. |
| Can it obtain that capability with no supplied instance? | `Denied.scala` | Compile error: no `Pay` instance in scope. | This is ordinary typed dependency resolution; alone it is not proof of complete mediation. |
| Can it hide a captured capability in a pure callback? | `CaptureDenied.scala` | Compile error: `pay` cannot flow into the empty capture set. | Demonstrates an actual capture-checking restriction in this tiny example. |
| Can it fabricate a capability by unchecked cast? | `CastDenied.scala` | Compile error: `asInstanceOf` unavailable in safe mode. | Other escape hatches and dependencies are not exhaustively tested. |
| Will two independently restored approved SDK states execute the effect twice? | `sdk_probe.py` | Two simulated effects with one serialized approved snapshot. | In-memory single-process example; production transaction semantics not assessed. |
| Can an application-owned effect ledger collapse this replay? | `idempotent_probe.py` | Two resumptions yielded one recorded effect. Reusing one call ID with changed arguments raised `ValueError`. | Shared in-memory lock and ledger; not durable or distributed. |
| Does the ledger enforce complete mediation? | `idempotent_probe.py` direct call | A separate direct call produced a second effect. | Every critical effect entry point must enforce the same approval and replay checks. |

The Scala tests were compiled with Scala CLI **1.17.1**, Scala **3.9.0**, Java 17, `--server=false --jvm system`; the exit codes were 0 for `Allowed` and 1 for all three intentional counterexamples. The dependency mirror in this execution environment was accessed through a temporary local forwarding proxy; it was only a transport aid and is not part of the artifact. Run `python -m benchmark.p3_binding.scala.run_scala` with `SCALA_CLI` and optionally `SCALA_REPOSITORY_URL` configured. Compile each fixture independently because each declares a class called `Pay`. These are compiler observations on these exact snippets, not a formal proof of Scala as a whole.

The SDK comparison used `openai-agents==0.22.3`, `socksio`, and an offline scripted model. Run `python -m benchmark.p3_binding.idempotent_probe` or `python -m unittest discover -s tests -v`. The Python test is optional and skipped if the SDK is absent. The ledger key is the host's workflow ID and the SDK tool call ID; a fingerprint of action plus canonicalized simple arguments prevents changing this key's payload. This probe presumes trusted workflow IDs, the integrity and ownership of restored state, and a trusted tool context. `Lock` makes the in-memory operation atomic inside one process; no database, distributed replay prevention, authenticated human, durable effect service, expiry, or crash recovery is modeled. The effect and ledger entry would need to be one atomic effect-side operation in a real implementation.

## Interpretation for P3*

Scala safe mode/capture checking can statically constrain *who holds the modeled effect capability*. It does not decide whether a real human approved a particular recipient and amount. The SDK can pause before a tool call, and an application-owned effect boundary can bind a unique call ID and argument fingerprint at execution time. Neither mechanism proves that an independent payment API or shell access cannot bypass the boundary; that is a whole-system mediation requirement.

This experiment demonstrates useful restrictions with existing language/runtime techniques. It offers **no evidence yet that a new programming language is required**. To test that hypothesis further, audit all privileged entry points in one constrained real application and independently review the trusted capability implementations. If complete mediation and exact approval binding can be obtained under acceptable engineering assumptions, stop the language proposal. If not, identify the irreducible missing guarantee rather than inventing syntax first.

Primary references: [Scala safe mode](https://docs.scala-lang.org/scala3/reference/experimental/capture-checking/safe.html), [Scala capture checking basics](https://docs.scala-lang.org/scala3/reference/experimental/capture-checking/basics.html), [OpenAI Agents SDK approval and persisted state](https://openai.github.io/openai-agents-python/human_in_the_loop/).
