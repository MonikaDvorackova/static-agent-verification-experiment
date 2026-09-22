@agent
def agent_fn(request):
    x = llm(request)
    if request:
        x = validate(x)
        x = human_approve(x)
    payment.execute(x)
