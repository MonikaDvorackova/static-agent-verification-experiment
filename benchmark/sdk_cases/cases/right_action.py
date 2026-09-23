from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    payment.execute(authorize_action('payment.execute', validate(llm(request))))
    return "done"

agent = Agent(name="case", tools=[action])
