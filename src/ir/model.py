from __future__ import annotations
import ast
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Instruction:
    node: ast.stmt
    line: int
    effects: frozenset[str] = frozenset()

@dataclass(frozen=True)
class Program:
    tree: ast.Module
    functions: dict[str, ast.FunctionDef]
    entries: tuple[str, ...]
    instructions: dict[str, tuple[Instruction, ...]]

@dataclass(frozen=True)
class Value:
    origins: frozenset[str] = frozenset()
    sensitive: bool = False
    validated: bool = False
    approved: bool = False
    unknown: bool = False
    effects: frozenset[str] = frozenset()

    def combine(self, other: Value) -> Value:
        return Value(self.origins | other.origins, self.sensitive or other.sensitive,
                     self.validated and other.validated, self.approved and other.approved,
                     self.unknown or other.unknown, self.effects | other.effects)

@dataclass
class State:
    env: dict[str, Value] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    uncertainty: list[str] = field(default_factory=list)
    findings: list[tuple[str, str]] = field(default_factory=list)
    returned: Value | None = None

    def copy(self) -> State:
        return State(self.env.copy(), self.aliases.copy(), self.uncertainty.copy(),
                     self.findings.copy(), self.returned)
