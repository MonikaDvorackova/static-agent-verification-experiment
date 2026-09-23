@agent
def agent_fn(request):
    result = validate(llm(request))
    approved = human_approve_action('db.mutate', result)
    payment.execute(approved)
