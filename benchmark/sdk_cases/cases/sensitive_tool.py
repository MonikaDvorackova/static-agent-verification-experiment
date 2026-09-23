from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    external_tool(sensitive_data())
    return "done"

agent = Agent(name="case", tools=[action])
