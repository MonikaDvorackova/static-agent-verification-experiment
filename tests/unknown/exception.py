@agent
def agent_fn(request):
    try:
        payment.execute(human_approve(validate(llm(request))))
    except Exception:
        payment.execute(request)
