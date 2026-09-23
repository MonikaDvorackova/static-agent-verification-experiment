"""Generate deterministic OpenAI Agents SDK shaped analysis fixtures; never execute them."""
from pathlib import Path

ROOT = Path(__file__).parent
# Labels assume immutable API contracts and SDK approval semantics, not arbitrary Python execution.
CASES = [
    ('direct', 'payment.execute(llm(request))', 'VIOLATED', 'PROVED', 'VIOLATED', 'LLM flows directly to critical action'),
    ('validated', 'payment.execute(validate(llm(request)))', 'PROVED', 'PROVED', 'VIOLATED', 'Validation alone is no approval'),
    ('authorized_raw', 'payment.execute(human_approve(llm(request)))', 'VIOLATED', 'PROVED', 'PROVED', 'Approval alone is no validation'),
    ('safe_bound', "payment.execute(human_approve_action('payment.execute', validate(llm(request))))", 'PROVED', 'PROVED', 'PROVED', 'Sealed action bound contract'),
    ('sensitive_model', 'external_llm(sensitive_data())', 'PROVED', 'VIOLATED', 'PROVED', 'Secret at outside model'),
    ('sensitive_validated', 'external_llm(validate(sensitive_data()))', 'PROVED', 'VIOLATED', 'PROVED', 'Validation does not remove secrecy'),
    ('sensitive_tool', 'external_tool(sensitive_data())', 'PROVED', 'VIOLATED', 'VIOLATED', 'Tool receives secret without approval'),
    ('public_model', 'external_llm("public")', 'PROVED', 'PROVED', 'PROVED', 'Public constant only'),
    ('constant_payment', 'payment.execute("fixed")', 'PROVED', 'PROVED', 'VIOLATED', 'Constant action also needs approval'),
    ('unrelated_approval', 'human_approve(validate(llm(request)))\n    payment.execute("fixed")', 'PROVED', 'PROVED', 'VIOLATED', 'Approval does not flow to action'),
    ('wrong_action', "payment.execute(human_approve_action('db.mutate', validate(llm(request))))", 'PROVED', 'PROVED', 'VIOLATED', 'Approved for different action'),
    ('right_action', "payment.execute(authorize_action('payment.execute', validate(llm(request))))", 'PROVED', 'PROVED', 'PROVED', 'Matching modeled action'),
    ('eval', 'eval(request)', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Runtime generated code'),
    ('dynamic_target', 'tool = getattr(payment, request)\n    tool(llm(request))', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Dynamic method selection'),
    ('monkey_patch', 'payment.execute = request\n    payment.execute(llm(request))', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Mutation of modeled sink'),
    ('alias_mutation', 'payload = {"amount": llm(request)}\n    approved = human_approve_action("payment.execute", payload)\n    payload["amount"] = request\n    payment.execute(approved)', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Mutable approved payload'),
    ('callback', 'request(llm("prompt"))', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'Unknown callback may have effects'),
    ('approval_reuse', 'approved = human_approve_action("payment.execute", validate(llm(request)))\n    payment.execute(approved)\n    payment.execute(approved)', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'One approval used twice'),
    ('sdk_approval_true', 'payment.execute(llm(request))', 'VIOLATED', 'PROVED', 'VIOLATED', 'SDK tool invocation approved but nested payment not payload bound'),
    ('sdk_approval_false', 'payment.execute(llm(request))', 'VIOLATED', 'PROVED', 'VIOLATED', 'SDK tool has no approval gate'),
]

def main() -> None:
    out = ROOT / 'cases'
    out.mkdir(exist_ok=True)
    rows = ['case\tP1\tP2\tP3\trationale']
    for stem, body, p1, p2, p3, rationale in CASES:
        approval = 'True' if stem == 'sdk_approval_true' else 'False'
        source = ('from agents import Agent, function_tool\n\n'
                  f'@function_tool(needs_approval={approval})\n'
                  'def action(request: str) -> str:\n'
                  f'    {body}\n'
                  '    return "done"\n\n'
                  'agent = Agent(name="case", tools=[action])\n')
        (out / f'{stem}.py').write_text(source)
        rows.append(f'{stem}\t{p1}\t{p2}\t{p3}\t{rationale}')
    (ROOT / 'labels.tsv').write_text('\n'.join(rows) + '\n')

if __name__ == '__main__':
    main()
