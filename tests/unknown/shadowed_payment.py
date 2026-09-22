@agent
def agent_fn(payment):
    payment.execute(human_approve(validate(llm('buy'))))
