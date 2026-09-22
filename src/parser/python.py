import ast
from pathlib import Path
from src.ir.model import Instruction, Program

EFFECTS = {'llm': {'LLM_CALL'}, 'external_llm': {'LLM_CALL'},
           'external_read': {'EXTERNAL_READ'}, 'external_tool': {'EXTERNAL_WRITE'},
           'fs.write': {'EXTERNAL_WRITE'}, 'db.mutate': {'EXTERNAL_WRITE', 'PRIVILEGED_ACTION'},
           'payment.execute': {'EXTERNAL_WRITE', 'PRIVILEGED_ACTION'},
           'human_approve': {'HUMAN_APPROVAL'}}

def name(expr: ast.expr) -> str | None:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        base = name(expr.value)
        return f'{base}.{expr.attr}' if base else None
    return None

def parse(source: str, filename: str = '<string>') -> Program:
    tree = ast.parse(source, filename=filename)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    entries = tuple(n.name for n in functions.values() if any(name(d) == 'agent' for d in n.decorator_list))
    instructions = {}
    for fn in functions.values():
        instructions[fn.name] = tuple(Instruction(s, s.lineno, frozenset().union(
            *(EFFECTS.get(name(c.func) or '', set()) for c in ast.walk(s) if isinstance(c, ast.Call)))) for s in fn.body)
    return Program(tree, functions, entries, instructions)
