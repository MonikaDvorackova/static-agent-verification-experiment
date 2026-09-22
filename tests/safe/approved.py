@agent
def agent_fn(request):
    result = llm(request)
    validated = validate(result)
    approved = human_approve(validated)
    payment.execute(approved)
