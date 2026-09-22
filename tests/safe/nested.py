def inner(x):
    return validate(x)

def outer(x):
    return human_approve(inner(x))

@agent
def agent_fn(request):
    payment.execute(outer(llm(request)))
