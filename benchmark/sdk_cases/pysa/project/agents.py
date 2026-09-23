from typing import Callable, Any

def function_tool(*, needs_approval: bool) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(fn: Callable[..., Any]) -> Callable[..., Any]:
        return fn
    return decorate

class Agent:
    def __init__(self, *, name: str, tools: list[Any]) -> None: ...
