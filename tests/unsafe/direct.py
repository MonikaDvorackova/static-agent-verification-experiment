@agent
def purchasing_agent(request):
    result = llm(request)
    payment.execute(result)
