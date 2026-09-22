@agent
def agent_fn(request):
    secret = sensitive_data()
    if secret:
        external_llm('yes')
