@agent
def agent_fn(request):
    approved = human_approve(llm(request))
    payment.execute(validate(approved))
