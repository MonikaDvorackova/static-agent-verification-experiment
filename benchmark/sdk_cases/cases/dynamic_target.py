from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    tool = getattr(payment, request)
    tool(llm(request))
    return "done"

agent = Agent(name="case", tools=[action])
