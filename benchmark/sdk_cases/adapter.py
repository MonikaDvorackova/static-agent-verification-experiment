"""Closed-world *experimental* AST adapter for a single SDK function tool.

No SDK code is executed. Results require sealed SDK and policy contracts, inert
built-in annotations, and the exact registration shape checked below.
"""
from __future__ import annotations
import ast
from src.analysis.engine import analyze
from src.diagnostics.result import Result


def analyze_tool(source: str, filename: str) -> tuple[Result, ...]:
    def unknown(reason: str) -> tuple[Result, ...]:
        return tuple(Result(p, 'UNKNOWN', (f'{filename}: {reason}',)) for p in ('P1', 'P2', 'P3'))

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return unknown(f'invalid Python: {exc}')
    if len(tree.body) != 3:
        return unknown('SDK profile requires one import, tool definition and registration')
    imp, fn, registration = tree.body
    if (not isinstance(imp, ast.ImportFrom) or imp.module != 'agents' or imp.level or
            {(a.name, a.asname) for a in imp.names} != {('Agent', None), ('function_tool', None)}):
        return unknown('unrecognized SDK import or alias')
    if not isinstance(fn, ast.FunctionDef) or len(fn.decorator_list) != 1:
        return unknown('single synchronous function tool required')
    decorator = fn.decorator_list[0]
    if (not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Name)
            or decorator.func.id != 'function_tool' or decorator.args
            or len(decorator.keywords) != 1 or decorator.keywords[0].arg != 'needs_approval'
            or not isinstance(decorator.keywords[0].value, ast.Constant)
            or type(decorator.keywords[0].value.value) is not bool):
        return unknown('unresolved tool decorator or dynamic approval policy')
    if (fn.args.defaults or fn.args.kw_defaults or fn.args.posonlyargs or fn.args.kwonlyargs
            or fn.args.vararg or fn.args.kwarg or len(fn.args.args) != 1):
        return unknown('unsupported tool signature')
    annotations = [fn.args.args[0].annotation, fn.returns]
    if not all(isinstance(a, ast.Name) and a.id == 'str' for a in annotations):
        return unknown('only inert built-in string annotations modeled')
    if (not isinstance(registration, ast.Assign) or len(registration.targets) != 1
            or not isinstance(registration.targets[0], ast.Name)
            or not isinstance(registration.value, ast.Call)
            or not isinstance(registration.value.func, ast.Name)
            or registration.value.func.id != 'Agent' or registration.value.args):
        return unknown('unresolved agent registration')
    keys = {k.arg: k.value for k in registration.value.keywords}
    if (set(keys) != {'name', 'tools'} or not isinstance(keys['name'], ast.Constant)
            or not isinstance(keys['name'].value, str)
            or not isinstance(keys['tools'], ast.List)
            or len(keys['tools'].elts) != 1
            or not isinstance(keys['tools'].elts[0], ast.Name)
            or keys['tools'].elts[0].id != fn.name):
        return unknown('dynamic tools list or agent configuration')
    # Approval of the SDK tool invocation is not authorization of effects inside
    # the tool. Therefore needs_approval is checked but grants no P3 token.
    transformed = ast.FunctionDef(
        name=fn.name, args=fn.args, body=fn.body,
        decorator_list=[ast.Name(id='agent', ctx=ast.Load())],
        returns=None, type_comment=None,
    )
    transformed.args.args[0].annotation = None
    module = ast.fix_missing_locations(ast.Module(body=[transformed], type_ignores=[]))
    return analyze(ast.unparse(module), filename)
