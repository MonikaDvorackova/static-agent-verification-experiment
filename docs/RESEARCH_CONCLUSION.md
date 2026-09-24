# Research conclusion: static verification of Python AI agents

24 September 2026. **Status: bounded research phase closed; results are experimental.** This project is architecturally independent of AIGov. This document is a decision record, not a claim of production security, a general impossibility theorem, or a new-language proposal. Source evidence and reproduction details live in the linked experiment documents.

## Question and decision

Can selected AI-agent safety and auditability properties be verified *before execution* for ordinary Python? **Only conditionally, for a restricted and externally trusted model.** On unchanged real agent modules, this analyzer did not establish P1, P2 or P3. In a deliberately sealed, authored subset it returned useful conditional PROVED/VIOLATED/UNKNOWN judgments. Existing static taint and capability techniques already address important parts of the question; exact human approval and complete effect mediation also depend on trusted runtime components.

**Decision: do not design a new language on current evidence. Stop extending this AST prototype solely to increase synthetic coverage.** Reopen that decision only if an independently reviewed comparison demonstrates a valuable guarantee that cannot be obtained under acceptable constraints with existing languages and effect mediators. No such gap has been demonstrated here.

## What was observed

| Experiment | Bounded observation | What it cannot establish |
|---|---|---|
| 28 authored Python fixtures (`tests/expectations.tsv`) | Three-valued rules and explicit UNKNOWN diagnostics exercise P1–P3 and adverse Python constructs. | Soundness for arbitrary Python or correctness of assumed library contracts. |
| 20 authored SDK-shaped cases (`SDK_PROFILE_EXPERIMENT.md`) | An AST adapter matched 60 internally authored conditional labels: 27 PROVED, 15 VIOLATED, 18 UNKNOWN; unadapted analyzer returned 60 UNKNOWN. | Independent ground truth, real-world false-PROVED rate, or verified SDK effects. |
| Instrumented Pysa baseline on those 20 cases | With the stated models, detected 4/4 known P1, 3/3 known P2 and 4/8 known P3 violations. | That other Pysa models or CodeQL cannot do better; absence of an alert is not PROVED. |
| Three pinned unchanged public agent modules (`MULTI_PROJECT_BENCHMARK.md`) | Original analyzer and narrow SDK adapter returned 18/18 UNKNOWN across three properties per module and two variants. Narrow CodeQL queries found two direct content-to-write flows and one scheduling edge. | Whole-application P1–P3 judgments; independent labels; a real-world Pysa/CodeQL accuracy comparison. |
| Offline SDK 0.22.3 approval probes (`P3_BINDING_EXPERIMENT.md`) | A rejected simulated tool did not execute; a permitted one did. Restoring two copies of one approved snapshot produced two effects in the controlled harness. | General SDK insecurity, authenticated reviewer identity, durable exactly-once behavior, or an actual payment. |
| Scala 3.9 safe-mode and effect-ledger probes (`CAPABILITY_COMPARISON.md`) | Capability-restricted example compiled; pure-closure capture and unsafe cast were rejected. An in-memory ledger collapsed two resumptions into one simulated effect. | Complete application confinement, durable transactional consumption, or concrete human intent. |
| Pinned Copane tool path (`REAL_APP_EFFECT_MEDIATION.md`) | Under an **analyst-defined** rule requiring approval for every agent-requested arbitrary file write, registered `run_command` wrote a temporary file without approval while `write_file` paused. | Copane's actual global policy or a whole-system P3* verdict; no third-party vulnerability classification is asserted. |

## What PROVED means here

An output labeled PROVED is conditional on a closed set of effectful entry points and immutable, independently checked contracts for sources, sinks and boundaries. Ordinary Python does not seal those names or guarantee that a recognized `validate` or `human_approve` implements the advertised semantics. Reflection, mutation, aliases, imports, decorators, dynamic dispatch and framework internals can invalidate the premise. Unresolved semantics require UNKNOWN with a reason. A syntactically demonstrated path within the model can be VIOLATED, but feasibility or actual impact outside that model needs separate evidence. See `FORMAL_MODEL.md` and `PYTHON_LIMITATIONS.md`.

The stronger P3* asks whether **each concrete critical effect** has an authentic, fresh, single-use approval bound to action, target, arguments and context, with every effect path mediated. A named approval call or one SDK tool's approval flag alone does not prove this. Static capability restrictions can confine *who may request an effect* within their safe subset; an audited effect service must bind and consume a specific decision at execution time. This is a design inference from the bounded experiments and existing techniques, not an implemented end-to-end proof.

## Limitations and publication threshold

The synthetic labels were produced by the authors of the analysis; the selected real paths were not independently labeled. There was no blind benchmark, exhaustive call graph, proof of complete mediation, authenticated human review, distributed crash/retry test, or proof about model correctness and external services. The prototype's IR records AST nodes and effects but does not implement a complete control/data-flow graph or effect type system. Do not publish a precision/recall figure for real agents from these data.

A paper or article may report the **negative result** and reproducible conditional experiments now, provided every number and policy is qualified as above. A stronger claim that a Python subset or a typed existing language suffices for P3* needs a closed effect inventory, independently stated policy and audited mediator. A claim that a *new language is required* additionally needs a demonstrated failure of reasonable existing-language restrictions, not merely difficulty analyzing arbitrary Python. The independent research workspace holds a separate topic and unpublished article outline; it remains distinct from this implementation repository and from AIGov.

## References and reproducibility

- [Formal model](FORMAL_MODEL.md); [SDK-shaped corpus](SDK_PROFILE_EXPERIMENT.md); [three-project comparison](MULTI_PROJECT_BENCHMARK.md); [P3* approval binding](P3_BINDING_EXPERIMENT.md); [capability comparison](CAPABILITY_COMPARISON.md); [real app mediation](REAL_APP_EFFECT_MEDIATION.md).
- Primary external documentation: [Pysa](https://pyre-check.org/docs/pysa-basics/), [CodeQL Python data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/), [Scala 3 safe mode](https://docs.scala-lang.org/scala3/reference/experimental/capture-checking/safe.html), [OpenAI Agents SDK approvals](https://openai.github.io/openai-agents-python/human_in_the_loop/).
