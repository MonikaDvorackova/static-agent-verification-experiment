@agent
def agent_fn(request):
    result = validate(llm(request))
    approved = human_approve_action(request, result)
    payment.execute(approved)
