@agent
def agent_fn(request):
    payment.execute(validate(llm(request)))
