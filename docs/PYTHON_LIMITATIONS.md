# Python limitations and experiment

The fixtures in `tests/unknown/` demonstrate dispatch, eval/exec, monkey patching, dynamic tool selection and exception handling. More counterexamples:

```python
validate = lambda x: x  # boundary name does not enforce a validator contract
payment.execute = lambda x: leak(x)  # sink meaning can change at runtime
getattr(payment, request.tool)(llm(request))  # target not statically fixed
exec('payment.execute(llm(request))')  # executable code absent from AST
```

Descriptors, metaclasses, import hooks, decorators, `__getattribute__`, module mutation, C extensions, arbitrary callbacks, context managers and import-time effects invalidate closed-world source reasoning. Aliases of mutable objects defeat simple variable flow. Exceptions and asynchronous tasks multiply paths. Source syntax cannot prove that a human actually approves, or that approval applies to the particular payment, or that validation rejects adversarial semantic payloads. The current prototype deliberately returns UNKNOWN for many of these constructs. A `PROVED` report is conditional on sealed imports, API contracts and limited syntax; it is not a whole-Python security guarantee. Future experiments should compare against CodeQL/Pysa/PyFlow and test precision on actual agent repositories before proposing a language.
