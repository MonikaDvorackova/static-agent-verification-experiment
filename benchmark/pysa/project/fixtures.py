"""Synthetic benchmark: trusted API stubs, not executable agent implementations."""
from typing import Any

def llm(prompt: Any) -> str: ...
def sensitive_data() -> str: ...
def validate(value: str) -> str: ...
def human_approve(value: str) -> str: ...
def payment_execute(value: str) -> None: ...
def external_llm(value: str) -> None: ...

def direct(request: str) -> None:
    payment_execute(llm(request))

def validated(request: str) -> None:
    payment_execute(validate(llm(request)))

def nested(request: str) -> None:
    payment_execute(human_approve(validate(llm(request))))

def sensitive() -> None:
    external_llm(sensitive_data())

def authorized_unvalidated(request: str) -> None:
    payment_execute(human_approve(llm(request)))
