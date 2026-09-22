@agent
def agent_fn(request):
    payment.execute(human_approve(llm(request)))
