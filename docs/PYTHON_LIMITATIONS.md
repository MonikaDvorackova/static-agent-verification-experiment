# Python limitations and experiment

The fixtures in `tests/unknown/` demonstrate dispatch, eval/exec, monkey patching, dynamic tool selection and exception handling. More counterexamples:

```python
validate = lambda x: x  # boundary name does not enforce a validator contract
payment.execute = lambda x: leak(x)  # sink meaning can change at runtime
getattr(payment, request.tool)(llm(request))  # target not statically fixed
exec('payment.execute(llm(request))')  # executable code absent from AST
```

Descriptors, metaclasses, import hooks, decorators, `__getattribute__`, module mutation, C extensions, arbitrary callbacks, context managers and import-time effects invalidate closed-world source reasoning. Aliases of mutable objects defeat simple variable flow. Exceptions and asynchronous tasks multiply paths. Source syntax cannot prove that a human actually approves, or that approval applies to the particular payment, or that validation rejects adversarial semantic payloads. The current prototype deliberately returns UNKNOWN for many of these constructs. A `PROVED` report is conditional on sealed imports, API contracts and limited syntax; it is not a whole-Python security guarantee. The controlled Pysa comparison and the three public examples are initial checks. Future work needs larger manually labeled agent repositories and custom framework models before accuracy or a language necessity can be assessed.

## Observed new adversarial cases

```python
@agent
def f(request):
    secret = sensitive_data()
    if secret:  # implicit control dependence; __bool__ can execute code
        external_llm("yes")

@agent
def g(request):
    approved = human_approve(validate(llm(request)))
    payment.execute(approved)
    db.mutate(approved)  # approval value reused for a distinct action

def hidden(x=payment.execute(llm("buy"))):
    pass  # default is evaluated at function definition time
```

The prototype returns UNKNOWN for these implicit, reuse and definition-time cases. Runtime annotations, descriptors, overloaded operators and framework import/decorator behavior also force UNKNOWN. The public-framework experiment in `PUBLIC_CODE_EXPERIMENT.md` yielded 9/9 UNKNOWN. The Pysa configuration in `BASELINE_COMPARISON.md` missed a constant critical action and an argument changed after approval; those are limitations of that specific rule, not proof that all existing static tools must miss them.
