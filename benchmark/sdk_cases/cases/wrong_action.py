from agents import Agent, function_tool

@function_tool(needs_approval=False)
def action(request: str) -> str:
    payment.execute(human_approve_action('db.mutate', validate(llm(request))))
    return "done"

agent = Agent(name="case", tools=[action])
