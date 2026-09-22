# P3: approval and effect comparison

P3 in this experiment is a syntactic value-flow rule: a modeled critical action must consume a value returned by a trusted approval/authorization boundary. It is not proof that a human saw the intended target, amount or recipient. The prototype now treats reuse of one approval result across two critical actions as UNKNOWN and considers post-approval validation a new, unapproved payload. It flags a constant critical action as VIOLATED; string concatenation after approval is UNKNOWN because Python may overload the operation. Neither check proves nonforgeability of the boundary.

Three approaches can capture different parts of the requirement:

| Approach | Can statically detect | Missing assumption or limitation |
|---|---|---|
| Configured taint analysis (Pysa rule 6103) | Unapproved *labeled* payload reaches critical sink; direct and unrelated-payload cases in our fixtures | Constant-valued actions and modification after sanitizer are missed by this configuration. More sophisticated query/model design may improve it. |
| Static capability/effect checking (e.g. Scala 3 tracked capabilities) | Code without a declared capability cannot perform the modeled effect, assuming type checking and complete mediation | Possession of a capability alone does not prove a human approved these exact arguments. Requires nonforgeable capability and typed, scoped authority. |
| Runtime policy/approval mediator | Can inspect actual target and arguments immediately before an effect, including model-generated and dynamic calls | Must intercept every effect and protect against bypass, races, and stale approvals; a single observed execution does not prove all possible paths. |

The likely useful design is a **combination**: a static effect/capability layer to restrict who can request an action, and complete runtime mediation to bind one approval to a concrete invocation. Existing languages and agent harnesses already implement substantial parts of this idea. This experiment does not establish a need for new syntax or a new general-purpose language.

References: [Pysa models](https://pyre-check.org/docs/pysa-basics/), [Scala capture checking](https://docs.scala-lang.org/scala3/reference/experimental/cc.html), [Tracked Capabilities for Safer Agents](https://arxiv.org/abs/2603.00991), [Aegis runtime interception](https://arxiv.org/abs/2603.12621).
