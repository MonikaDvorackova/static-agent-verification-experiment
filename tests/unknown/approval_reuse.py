@agent
def agent_fn(request):
    approved = human_approve(validate(llm(request)))
    payment.execute(approved)
    db.mutate(approved)
