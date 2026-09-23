@agent
def agent_fn(request):
    result = validate(llm(request))
    approved = human_approve_action('payment.execute', result)
    payment.execute(approved)
