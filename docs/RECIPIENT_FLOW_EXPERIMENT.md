# Recipient-bound sensitive-data flow: comparison experiment

24 September 2026. Independent of AIGov. **Bounded model, not a language proposal.** The target is narrower than P2: for a closed inventory of external model recipients, a modeled sensitive value can be sent only when a grant names both that value and that recipient. This does not assert that the recipient is legally or organizationally authorized; issuance of a grant is an explicit trusted assumption.

## Implementations and status

1. `benchmark/recipient_flow/model.py` is an executable tiny instruction IR with `Secret`, `Public`, `Grant`, `Send` and `UnknownCall`. It checks a fixed instruction list before the simulated host records any effect. `PROVED` means only that all instructions in this *closed* list meet the stated grant relation. `VIOLATED` records a concrete modeled send with no matching grant. Unresolved dispatch, unknown values/recipients and unsupported instructions yield `UNKNOWN` with a reason. Python's normal import, reflection and direct I/O can bypass this host. Grants are ordinary dataclasses supplied to `check`: a malicious Python caller can construct one, so this example **does not establish unforgeability or real authorization**.
2. `benchmark/recipient_flow/scala/RecipientFlow.scala` sketches the equivalent boundary in an existing typed language. **It was not compiled in this environment** (no Scala CLI available); its private constructors and capability parameter alone do not prove issuance, complete mediation, or the requested grant's binding to the exact secret. It is a comparison candidate, not a positive compiler result. Prior *distinct* Scala compiler observations are recorded in `CAPABILITY_COMPARISON.md`.

## Adversarial outcomes

| Case | Expected / observed within the IR model | Reason |
|---|---|---|
| Correct recipient and secret grant | PROVED | Exact match in the closed input. |
| Sensitive send without grant | VIOLATED | Missing grant. |
| Grant for different recipient | VIOLATED | Recipient mismatch. |
| Grant for different secret | VIOLATED | Value identity mismatch. |
| Public data to known recipient | PROVED | No sensitive value. |
| Dynamically selected call | UNKNOWN | Call target unresolved. |
| Dynamically selected recipient | UNKNOWN | Outside known recipient inventory. |
| Valid send followed by invalid send | VIOLATED, zero recorded effects | Preflight checks the complete list before the host loop. |

Run `python -m unittest tests.test_recipient_flow -v`. The test covers the model and its Python simulation; it does not compile the Scala file, access a real model, or establish that all host effects are mediated.

## Escape routes and decision

The IR can be bypassed by direct Python I/O, the ordinary `Grant` constructor can be called by an adversary, and aliases or callbacks can hide effects outside the instruction list. A host that first sends and only later checks another instruction would lose the experiment's atomic preflight behavior. A grant can also be replayed because no single-use semantics are implemented. These are assumptions of the closed model, not solved security properties. Even a complete type check cannot determine whether a reviewer intended a particular disclosure or whether a remote provider respects confidentiality.

**Decision:** this executable result demonstrates a useful closed-language check but no advantage over existing typed capability boundaries plus a trusted host. The existing-language candidate has not been compiled or compared empirically here. Do not claim that a new language is necessary. A defensible next comparison requires a compiling Scala implementation with audited grant issuance, confinement of *all* network and tool effects, and equivalent adversarial tests; only a measured irreducible gap would reopen language design.
