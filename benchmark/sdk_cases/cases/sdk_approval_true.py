from agents import Agent, function_tool

@function_tool(needs_approval=True)
def action(request: str) -> str:
    payment.execute(llm(request))
    return "done"

agent = Agent(name="case", tools=[action])
