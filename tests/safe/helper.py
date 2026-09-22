def gate(x):
    return human_approve(validate(x))

@agent
def agent_fn(request):
    payment.execute(gate(llm(request)))
