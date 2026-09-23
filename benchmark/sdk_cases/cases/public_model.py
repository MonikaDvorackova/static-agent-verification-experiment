from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    external_llm("public")
    return "done"

agent = Agent(name="case", tools=[action])
