"""Reproduce the narrow P3 action-binding observations without executing agents."""
from __future__ import annotations

from src.analysis.engine import analyze


CASES = {
    "matching_literal": """@agent
def agent_fn(request):
    approved = human_approve_action('payment.execute', validate(llm(request)))
    payment.execute(approved)
""",
    "wrong_action": """@agent
def agent_fn(request):
    approved = human_approve_action('db.mutate', validate(llm(request)))
    payment.execute(approved)
""",
    "dynamic_action": """@agent
def agent_fn(request, chosen):
    approved = human_approve_action(chosen, validate(llm(request)))
    payment.execute(approved)
""",
    "reused_approval": """@agent
def agent_fn(request):
    approved = human_approve_action('payment.execute', validate(llm(request)))
    payment.execute(approved)
    payment.execute(approved)
""",
    "alias_modified_after_approval": """@agent
def agent_fn(request):
    payload = validate(llm(request))
    approved = human_approve_action('payment.execute', payload)
    payload['recipient'] = request
    payment.execute(approved)
""",
    "unmediated_effect": """@agent
def agent_fn(request):
    approved = human_approve_action('payment.execute', validate(llm(request)))
    payment.execute(approved)
    import os
    os.system('transfer')
""",
}


def results() -> dict[str, tuple[str, str]]:
    return {
        case: (
            next(r.status for r in analyze(code, f'{case}.py') if r.property == 'P3'),
            # Strict P3* requires concrete target/argument binding, authentic issuer,
            # freshness, single use and complete mediation. None is certified here.
            'UNKNOWN',
        )
        for case, code in CASES.items()
    }


if __name__ == '__main__':
    for case, (prototype, strict) in results().items():
        print(f'{case}\t{prototype}\t{strict}')
