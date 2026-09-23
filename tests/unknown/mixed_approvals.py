@agent
def agent_fn(request):
    result = validate(llm(request))
    payment_approved = human_approve_action('payment.execute', result)
    generic_approved = human_approve(result)
    payment.execute((payment_approved, generic_approved))
