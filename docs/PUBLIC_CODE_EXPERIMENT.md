# Unmodified agent-framework examples, 22 September 2026

We fetched three public, official Python examples, parsed their source without installing their dependencies, and ran `analyze(source, filename)`. No example was modified, executed or included in this repository. The exact fetched blob SHA identifies the bytes evaluated. This is a **coverage check**, not ground-truth security labeling; no vulnerability or safety assertion is made about these projects.

| Source | Fetched blob SHA | P1 | P2 | P3 | Main reason |
|---|---|---|---|---|---|
| [OpenAI Agents SDK `examples/basic/tools.py`](https://github.com/openai/openai-agents-python/blob/main/examples/basic/tools.py) | `3a465bb7057d69a37fa7e64ff22ae5036d71bce0` | UNKNOWN | UNKNOWN | UNKNOWN | SDK imports, `@tool`, runtime `Agent(tools=...)`, no modeled top-level `@agent` function |
| [LangGraph integration `tools_agent.py`](https://github.com/langchain-ai/langgraph/blob/main/libs/sdk-py/integration/graph/tools_agent.py) | `a4aeb5649996ce38e686e050dd00383af0b73452` | UNKNOWN | UNKNOWN | UNKNOWN | Imports, subclassed fake model and `create_agent(tools=...)`, no modeled entry point |
| [CrewAI example `crew.py`](https://github.com/crewAIInc/crewAI-examples/blob/main/crews/meta_quest_knowledge/src/meta_quest_knowledge/crew.py) | `8299e07e6c16c6bde48f2de2682f6b6bb5932e38` | UNKNOWN | UNKNOWN | UNKNOWN | Imports, class decorators and configuration-driven crew, no modeled top-level entry point |

Aggregate: **0/9 PROVED, 0/9 VIOLATED, 9/9 UNKNOWN**. All three examples differ from the prototype's stipulated API. No attempt was made to map their concrete model calls, source labels, authorization rules or sinks. The experiment establishes near-zero out-of-box applicability to these examples, not a measured false-positive/false-negative rate. A meaningful framework evaluation needs trusted SDK models, explicit entry-point discovery, sink classification, hand-labeled reachable actions and a comparison against existing analyzers. It should retain UNKNOWN for unresolved framework behavior.
