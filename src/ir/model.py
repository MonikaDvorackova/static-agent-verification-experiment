from __future__ import annotations
import ast
from dataclasses import dataclass, field
from enum import Enum


class Trust(str, Enum):
    TRUSTED = 'Trusted'
    UNTRUSTED = 'Untrusted'
    UNKNOWN = 'Unknown'


class Sensitivity(str, Enum):
    PUBLIC = 'Public'
    SENSITIVE = 'Sensitive'

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
    approval_id: int | None = None
    approval_target: str | None = None

    @property
    def trust(self) -> Trust:
        if self.unknown:
            return Trust.UNKNOWN
        return (Trust.UNTRUSTED if self.origins & {'LLM', 'external', 'user'}
                else Trust.TRUSTED)

    @property
    def sensitivity(self) -> Sensitivity:
        return Sensitivity.SENSITIVE if self.sensitive else Sensitivity.PUBLIC

    def combine(self, other: Value) -> Value:
        return Value(self.origins | other.origins, self.sensitive or other.sensitive,
                     self.validated and other.validated, self.approved and other.approved,
                     self.unknown or other.unknown or (self.approved and other.approved and
                     (self.approval_id != other.approval_id or self.approval_target != other.approval_target)),
                     self.effects | other.effects,
                     self.approval_id if self.approval_id == other.approval_id else None,
                     self.approval_target if self.approval_target == other.approval_target else None)

@dataclass
class State:
    env: dict[str, Value] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    uncertainty: list[str] = field(default_factory=list)
    findings: list[tuple[str, str]] = field(default_factory=list)
    returned: Value | None = None
    consumed_approvals: set[int] = field(default_factory=set)

    def copy(self) -> State:
        return State(self.env.copy(), self.aliases.copy(), self.uncertainty.copy(),
                     self.findings.copy(), self.returned, self.consumed_approvals.copy())
