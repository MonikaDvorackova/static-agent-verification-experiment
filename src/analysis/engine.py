from __future__ import annotations
import ast
from src.ir.model import Program, State, Value
from src.parser.python import parse, name
from src.policies.contracts import SINKS, SOURCES, BOUNDARIES

CONTRACT_ROOTS = {n.split('.')[0] for n in (*SINKS, *SOURCES, *BOUNDARIES)}
from src.diagnostics.result import Result

class Analyzer:
    def __init__(self, program: Program, filename: str):
        self.program, self.filename = program, filename

    def reason(self, node: ast.AST, message: str) -> str:
        return f'{self.filename}:{getattr(node, "lineno", 0)}: {message}'

    def expression(self, node: ast.expr, state: State, stack: tuple[str, ...]) -> Value:
        if isinstance(node, ast.Constant):
            return Value()
        if isinstance(node, ast.Name):
            return state.env.get(node.id, Value(unknown=True))
        if isinstance(node, (ast.Tuple, ast.List, ast.Set, ast.Dict, ast.BinOp,
                             ast.UnaryOp, ast.Compare, ast.Subscript, ast.JoinedStr)):
            children = [c for c in ast.iter_child_nodes(node) if isinstance(c, ast.expr)]
            values = [self.expression(c, state, stack) for c in children]
            if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare, ast.Subscript,
                                 ast.JoinedStr)) and any(not isinstance(c, ast.Constant) for c in children):
                state.uncertainty.append(self.reason(node, f'overloaded Python operation: {type(node).__name__}'))
            combined = values[0] if values else Value()
            for v in values[1:]:
                combined = combined.combine(v)
            return combined
        if isinstance(node, ast.Attribute):
            state.uncertainty.append(self.reason(node, 'unresolved attribute read'))
            return Value(unknown=True)
        if not isinstance(node, ast.Call):
            state.uncertainty.append(self.reason(node, f'unsupported expression {type(node).__name__}'))
            return Value(unknown=True)
        target = name(node.func)
        if isinstance(node.func, ast.Name):
            target = state.aliases.get(node.func.id, target)
        args = [self.expression(a, state, stack) for a in node.args]
        if node.keywords:
            state.uncertainty.append(self.reason(node, 'keyword call semantics unsupported'))
            args.extend(self.expression(k.value, state, stack) for k in node.keywords)
        data = args[0] if args else Value()
        for v in args[1:]:
            data = data.combine(v)
        if target in ('eval', 'exec', '__import__', 'getattr', 'setattr', 'globals', 'locals') or target is None:
            state.uncertainty.append(self.reason(node, f'dynamic call or dispatch: {target or "computed target"}'))
            return Value(data.origins, data.sensitive, unknown=True)
        if target in SOURCES:
            kind = SOURCES[target]
            return Value(data.origins | {kind}, data.sensitive or kind == 'local-sensitive',
                         unknown=data.unknown, effects=data.effects | ({'LLM_CALL'} if target == 'llm' else {'EXTERNAL_READ'} if target == 'external_read' else set()))
        if target in BOUNDARIES:
            if len(args) != 1:
                state.uncertainty.append(self.reason(node, f'{target} requires exactly one payload'))
                return Value(data.origins, data.sensitive, unknown=True)
            return Value(data.origins, data.sensitive,
                         data.validated or BOUNDARIES[target] == 'validation',
                         BOUNDARIES[target] == 'authorization', data.unknown,
                         data.effects | ({'HUMAN_APPROVAL'} if target == 'human_approve' else set()),
                         id(node) if BOUNDARIES[target] == 'authorization' else None)
        if target in SINKS:
            if not args:
                state.uncertainty.append(self.reason(node, f'{target} has no modeled payload'))
            else:
                for prop in SINKS[target]:
                    if prop == 'P1' and 'LLM' in data.origins and not data.validated:
                        state.findings.append((prop, self.reason(node, f'unvalidated LLM output reaches {target}')))
                    if prop == 'P2' and data.sensitive:
                        state.findings.append((prop, self.reason(node, f'sensitive data reaches unauthorized {target}')))
                    if prop == 'P3' and not data.approved:
                        state.findings.append((prop, self.reason(node, f'critical action {target} lacks payload-bound authorization')))
                if 'P3' in SINKS[target] and data.approved:
                    if data.approval_id is None:
                        state.uncertainty.append(self.reason(node, 'approval identity lost during data combination'))
                    elif data.approval_id in state.consumed_approvals:
                        state.uncertainty.append(self.reason(node, 'authorization result reused for another critical action'))
                    else:
                        state.consumed_approvals.add(data.approval_id)
                if data.unknown:
                    state.uncertainty.append(self.reason(node, f'unknown payload at {target}'))
            return Value(effects=data.effects | {'EXTERNAL_WRITE'})
        if target in self.program.functions:
            if target in stack or len(stack) > 12:
                state.uncertainty.append(self.reason(node, f'recursive or excessive call depth: {target}'))
                return Value(unknown=True)
            fn = self.program.functions[target]
            if len(fn.args.args) != len(args):
                state.uncertainty.append(self.reason(node, f'call signature unresolved: {target}'))
                return Value(unknown=True)
            local = State(dict(zip((p.arg for p in fn.args.args), args)))
            paths = self.block(fn.body, [local], stack + (target,))
            for path in paths:
                state.findings.extend(path.findings)
                state.uncertainty.extend(path.uncertainty)
            if len(paths) == 1 and paths[0].returned is not None:
                state.consumed_approvals.update(paths[0].consumed_approvals)
                return paths[0].returned
            state.uncertainty.append(self.reason(node, f'return paths unresolved: {target}'))
            return Value(unknown=True)
        state.uncertainty.append(self.reason(node, f'unresolved call: {target}'))
        return Value(data.origins, data.sensitive, unknown=True)

    def block(self, body: list[ast.stmt], states: list[State], stack: tuple[str, ...]) -> list[State]:
        for stmt in body:
            next_states: list[State] = []
            for state in states:
                if state.returned is not None:
                    next_states.append(state)
                    continue
                if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                    value = self.expression(stmt.value, state, stack) if stmt.value else Value(unknown=True)
                    targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                    for t in targets:
                        if isinstance(t, ast.Name):
                            state.env[t.id] = value
                            alias = name(stmt.value) if isinstance(stmt.value, (ast.Name, ast.Attribute)) else None
                            if alias in SINKS or alias in SOURCES or alias in BOUNDARIES:
                                state.aliases[t.id] = alias
                            else:
                                state.aliases.pop(t.id, None)
                        else:
                            state.uncertainty.append(self.reason(stmt, 'mutation or aliasing through complex assignment'))
                    next_states.append(state)
                elif isinstance(stmt, ast.Expr):
                    self.expression(stmt.value, state, stack)
                    next_states.append(state)
                elif isinstance(stmt, ast.Return):
                    state.returned = self.expression(stmt.value, state, stack) if stmt.value else Value()
                    next_states.append(state)
                elif isinstance(stmt, ast.If):
                    condition = self.expression(stmt.test, state, stack)
                    if not isinstance(stmt.test, ast.Constant):
                        # __bool__/__len__ may execute arbitrary Python; a tainted
                        # condition can also leak through control dependence.
                        state.uncertainty.append(self.reason(stmt.test, 'dynamic truthiness or implicit control flow'))
                    if not isinstance(stmt.test, ast.Constant) or bool(stmt.test.value):
                        next_states.extend(self.block(stmt.body, [state.copy()], stack))
                    if not isinstance(stmt.test, ast.Constant) or not bool(stmt.test.value):
                        next_states.extend(self.block(stmt.orelse, [state.copy()], stack))
                elif isinstance(stmt, ast.Pass):
                    next_states.append(state)
                else:
                    state.uncertainty.append(self.reason(stmt, f'unsupported control flow: {type(stmt).__name__}'))
                    next_states.append(state)
            states = next_states
            if len(states) > 128:
                for state in states[:1]:
                    state.uncertainty.append(self.reason(stmt, 'path limit exceeded'))
                states = states[:1]
        return states

    def run(self) -> tuple[Result, ...]:
        global_uncertainty: list[str] = []
        for stmt in self.program.tree.body:
            if isinstance(stmt, ast.FunctionDef):
                if stmt.args.defaults or any(x is not None for x in stmt.args.kw_defaults):
                    global_uncertainty.append(self.reason(stmt, f'function default expression at definition time: {stmt.name}'))
                annotations = [a.annotation for a in (*stmt.args.posonlyargs, *stmt.args.args,
                               *stmt.args.kwonlyargs) if a.annotation is not None]
                if stmt.returns is not None or annotations:
                    global_uncertainty.append(self.reason(stmt, f'runtime annotation semantics not modeled: {stmt.name}'))
                if stmt.name in CONTRACT_ROOTS or any(a.arg in CONTRACT_ROOTS for a in stmt.args.args):
                    global_uncertainty.append(self.reason(stmt, f'contract name shadowed in {stmt.name}'))
                for nested in ast.walk(stmt):
                    if isinstance(nested, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                        targets = nested.targets if isinstance(nested, ast.Assign) else [nested.target]
                        if any(isinstance(t, ast.Name) and t.id in CONTRACT_ROOTS or isinstance(t, ast.Attribute) and (name(t) or '').split('.')[0] in CONTRACT_ROOTS for t in targets):
                            global_uncertainty.append(self.reason(nested, 'modeled API name may be rebound or monkey patched'))
                if any(name(d) not in ('agent',) for d in stmt.decorator_list):
                    global_uncertainty.append(self.reason(stmt, f'unknown decorator on {stmt.name}'))
            else:
                global_uncertainty.append(self.reason(stmt, 'module initialization or mutation not modeled'))
        if not self.program.entries:
            global_uncertainty.append(f'{self.filename}: no @agent entry point')
        paths: list[State] = []
        for entry in self.program.entries:
            fn = self.program.functions[entry]
            initial = State({a.arg: Value(origins=frozenset({'user'}), unknown=False) for a in fn.args.args})
            paths += self.block(fn.body, [initial], (entry,))
        results = []
        for prop in ('P1', 'P2', 'P3'):
            violations = sorted({reason for s in paths for p, reason in s.findings if p == prop})
            uncertainty = sorted(set(global_uncertainty + [r for s in paths for r in s.uncertainty]))
            status = 'UNKNOWN' if uncertainty else 'VIOLATED' if violations else 'PROVED'
            results.append(Result(prop, status, tuple(uncertainty if uncertainty else violations)))
        return tuple(results)

def analyze(source: str, filename: str = '<string>') -> tuple[Result, ...]:
    return Analyzer(parse(source, filename), filename).run()
