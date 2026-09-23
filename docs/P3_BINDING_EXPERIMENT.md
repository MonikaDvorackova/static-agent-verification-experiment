# P3 approval binding: bounded follow-up

23 September 2026. This is a research specification and a reproducible probe of the **existing** analyzer, not a proof that any SDK, language, or approval service enforces the specification. Run `python -m benchmark.p3_binding.run`. The six agent snippets are static input; no agent, payment, model, or shell command executes. The second column printed by the script is the prototype's modeled P3 verdict. The last column is the conservative assessment for the stronger requirement below; it is **not** another implemented checker.

## A stronger requirement, P3*

Let a concrete critical effect event be `effect(call_id, actor, action, target, args, context, time)`. P3* requires a prior authentic `approve(token, actor, action, target, canonical(args), context, expiry)` such that (1) the issuer is an authorized human or policy principal, (2) every field matches the executed invocation, (3) approval remains fresh at effect time, (4) the token is consumed atomically at most once, and (5) every critical effect crosses a mediator that checks these conditions immediately before the effect. Approval must not be inferred merely from a shared value or an earlier call in the same function. This is a proposed **operational** property: proving code calls an approval API is weaker than proving the API's authority, canonicalization, atomicity and mediation.

The existing P3 checks whether the sink consumes the return value of a modeled approval call; `human_approve_action` additionally carries a literal nominal sink name. It does not inspect recipient, amount, principal, context, freshness, or the executed tool's identity. Even `PROVED` means only a conditional result in the deliberately sealed, named-function model. In general Python code, a checker cannot infer a nonforgeable approval boundary from a function's spelling.

## Controlled cases

| Case | Existing P3 | P3* evidence | Unestablished condition |
|---|---|---|---|
| `matching_literal` | PROVED | UNKNOWN | Same action name and returned object do not prove concrete arguments, issuer, freshness, or complete mediation. |
| `wrong_action` | VIOLATED | UNKNOWN unconditionally | The modeled mismatch is a useful counterexample **assuming** the boundary really has the stated contract; real target resolution and API identity are not established. |
| `dynamic_action` | UNKNOWN | UNKNOWN | The approval target comes from a parameter. |
| `reused_approval` | UNKNOWN | UNKNOWN | No atomic, one-use approval token is established. |
| `alias_modified_after_approval` | UNKNOWN | UNKNOWN | An alias could mutate arguments after review; in this snippet even the meaning of `request` is not fixed. |
| `unmediated_effect` | UNKNOWN | UNKNOWN | An independent shell effect can bypass the recognized payment sink; an import and external effect are not modeled. |

The example with a matching literal is the sharpest gap: its `PROVED` verdict does **not** imply P3*. The outcome of P3* is conservatively UNKNOWN for every case because no complete effect inventory or authenticated mediator is supplied. A concrete P3* violation could be established by supplying executable contracts, an effect trace, or a closed-world model and demonstrating a feasible bad path. These six static snippets alone are not that evidence.

## Comparison against existing mechanisms

| Mechanism | What is supported by source or our experiment | What remains to establish P3* |
|---|---|---|
| CodeQL Python global data flow / taint tracking | Configurable path queries can model sources and sinks; our three-project study found two direct write flows and one separate scheduling edge. | A data-flow path alone cannot authenticate an approver or prove every concrete effect goes through the same approval gate. A richer framework-specific model could check some call ordering; **not tested here**. |
| OpenAI Agents SDK `needs_approval` | Its documented runner interrupts the tool call for approval; a callable condition receives the parsed parameters and call ID. An offline executable probe is now described below. | Audit all effect entry points; verify approver identity, snapshot ownership/integrity, expiry and exactly-once handling across resumptions. |
| Scala 3 capture checking safe mode / typed capability API | Documentation describes static tracking of capabilities and a capability-safe subset. It can restrict effects mediated by the typed API if no unsafe bypass exists. | A capability type by itself does not attest the approving human, concrete effect arguments, freshness or single use. **No Scala program compiled here.** |
| Current AST prototype | Executes the six probes deterministically, checks nominal approval names and flags some uncertainty. | Does not verify its sealed-contract premise or P3*. `PROVED` is a conditional modeling claim, not real Python or SDK certification. |

Sources: [CodeQL Python data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/), [OpenAI Agents SDK approval guide](https://openai.github.io/openai-agents-python/human_in_the_loop/), [SDK tool reference](https://openai.github.io/openai-agents-python/ref/tool/), [Scala 3 safe mode](https://docs.scala-lang.org/scala3/reference/experimental/capture-checking/safe.html).

## Research decision

Current evidence supports a **static capability restriction plus a runtime approval mediator**, provided every critical effect uses the restricted capability and the mediator binds a fresh approval to the exact invocation. This is an architectural hypothesis, not a verified end-to-end implementation. The next decisive test is a typed capability implementation and an SDK mediator with authenticated, atomic consumption, a deliberately separate direct-effect path and changed targets. Record any remaining bypasses and assumptions before considering another analyzer rule. There is presently **no evidence that a new programming language is necessary**. If existing typed subsets plus complete runtime mediation meet P3* under clear assumptions, stop the language proposal.

## Offline SDK execution (OpenAI Agents SDK 0.22.3)

Install in an isolated environment with `pip install 'openai-agents==0.22.3' socksio`, then run `python -m benchmark.p3_binding.sdk_probe` and `python -m unittest discover -s tests -v`. A deterministic scripted `Model` emits one `pay` tool call; the tool only appends to an in-memory list. No OpenAI API, real payment or remote service is called; tracing is disabled. With `needs_approval=True`, both runs paused before the effect. Rejection left the list empty; approval resumed and recorded one call with `Alice, 10`. The pending interruption carried these arguments.

**Replay probe:** serializing the approved pending `RunState`, restoring the same snapshot twice, and resuming each copy with the same agent and model recorded **two** simulated effects with `Alice, 10`. This demonstrates that the application cannot assume cross-restore exactly-once effects from the SDK approval alone. These are two independent resume lineages from one saved snapshot; we did not test an ordinary repeated continuation of a single live run. It does not imply the SDK lacks defenses against other kinds of replay, nor that a production service would lack its own idempotency key.

**Single-field mutation probe:** changing only `model_responses[0].output[0].arguments` in the approved serialized snapshot from `Alice, 10` to `Mallory, 100` resulted in a resumed call with the **original** `Alice, 10`. The pending call appears in multiple snapshot locations; this probe does not test coordinated tampering, authentication, or the full SDK validation rules. It establishes no general integrity guarantee. The SDK guide explicitly warns that deserialization does not authenticate the snapshot or the party submitting it; trusted storage or independently verified ownership and integrity are necessary.

The SDK experiment shows a working **runtime** tool gate and a concrete cross-restore replay risk for non-idempotent effects. It does not statically verify complete mediation, identify a human approver, or implement a P3* verifier. Its observation is limited to the pinned SDK version and the recorded scripts.
