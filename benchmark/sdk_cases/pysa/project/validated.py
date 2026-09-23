from agents import Agent, function_tool
from api import (llm, sensitive_data, validate, human_approve, human_approve_action, authorize_action, external_llm, external_tool, payment, db)

@function_tool(needs_approval=False)
def action(request: str) -> str:
    payment.execute(validate(llm(request)))
    return "done"

agent = Agent(name="case", tools=[action])
