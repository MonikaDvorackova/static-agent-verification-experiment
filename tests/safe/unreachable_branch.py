@agent
def agent_fn(request):
    if False:
        payment.execute(llm(request))
    else:
        payment.execute(human_approve(validate(llm(request))))
