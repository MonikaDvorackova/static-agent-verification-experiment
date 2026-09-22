def validate(x):
    return x

@agent
def agent_fn(request):
    payment.execute(human_approve(validate(llm(request))))
