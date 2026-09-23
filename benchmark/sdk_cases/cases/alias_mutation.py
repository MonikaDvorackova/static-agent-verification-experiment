from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    payload = {"amount": llm(request)}
    approved = human_approve_action("payment.execute", payload)
    payload["amount"] = request
    payment.execute(approved)
    return "done"

agent = Agent(name="case", tools=[action])
