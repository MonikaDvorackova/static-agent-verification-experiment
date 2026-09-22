@agent
def agent_fn(request):
    payload = validate(llm(request))
    payment.execute(human_approve(payload + request))
