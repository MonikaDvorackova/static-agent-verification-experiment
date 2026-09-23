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
| OpenAI Agents SDK `needs_approval` | Its documented runner interrupts the tool call for approval; a callable condition receives the parsed parameters and call ID. | Audit the exact SDK/tool versions, all effect entry points and any independent direct calls; verify who approves, whether changed inputs can be executed, persistence/expiry and replay behavior. **No SDK execution performed here.** |
| Scala 3 capture checking safe mode / typed capability API | Documentation describes static tracking of capabilities and a capability-safe subset. It can restrict effects mediated by the typed API if no unsafe bypass exists. | A capability type by itself does not attest the approving human, concrete effect arguments, freshness or single use. **No Scala program compiled here.** |
| Current AST prototype | Executes the six probes deterministically, checks nominal approval names and flags some uncertainty. | Does not verify its sealed-contract premise or P3*. `PROVED` is a conditional modeling claim, not real Python or SDK certification. |

Sources: [CodeQL Python data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/), [OpenAI Agents SDK approval guide](https://openai.github.io/openai-agents-python/human_in_the_loop/), [SDK tool reference](https://openai.github.io/openai-agents-python/ref/tool/), [Scala 3 safe mode](https://docs.scala-lang.org/scala3/reference/experimental/capture-checking/safe.html).

## Research decision

Current evidence supports a **static capability restriction plus a runtime approval mediator**, provided every critical effect uses the restricted capability and the mediator binds a fresh approval to the exact invocation. This is an architectural hypothesis, not a verified end-to-end implementation. The next decisive test is a small executable SDK tool with a deliberately separate direct-effect path, argument mutation, replay, and changed target; then attempt to close those paths using existing SDK and typed capability mechanisms. Record any remaining bypasses and assumptions before considering another analyzer rule. There is presently **no evidence that a new programming language is necessary**. If existing typed subsets plus complete runtime mediation meet P3* under clear assumptions, stop the language proposal.
