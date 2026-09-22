@agent
def agent_fn(request):
    x = [llm(request)]
    alias = x
    alias[0] = request
    payment.execute(human_approve(validate(x)))
