@agent
def agent_fn(request):
    tools[request](llm(request))
