@agent
def agent_fn(request):
    tool = getattr(payment, request)
    tool(llm(request))
