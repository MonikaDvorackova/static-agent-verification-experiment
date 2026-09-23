from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    approved = human_approve_action("payment.execute", validate(llm(request)))
    payment.execute(approved)
    payment.execute(approved)
    return "done"

agent = Agent(name="case", tools=[action])
