@agent
def agent_fn(request):
    payment.execute = lambda x: x
    payment.execute(human_approve(validate(llm(request))))
