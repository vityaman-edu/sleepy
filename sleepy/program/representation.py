from dataclasses import dataclass
from typing import override

from sleepy.core import UID, Identifiable


class ProgramNode(Identifiable):
    @property
    @override
    def uid(self) -> UID:
        return UID(id(self))


class Expression(ProgramNode):
    pass


@dataclass
class Program(ProgramNode):
    statements: list[Expression]


class Atom(Expression):
    pass


@dataclass
class Symbol(Atom):
    name: str


@dataclass
class Integer(Atom):
    value: int


@dataclass
class Kind(ProgramNode):
    name: str


@dataclass
class Parameter(Atom):
    name: Symbol
    kind: Kind


@dataclass
class Intrinsic(Atom):
    name: Symbol
    parameters: list[Parameter]
    return_kind: Kind


@dataclass
class Closure(Expression):
    from .namespace import Namespace

    parameters: list[Parameter]
    statements: list[Expression]
    namespace: Namespace


@dataclass
class Conditional(Expression):
    condition: Expression
    then_branch: Expression
    else_branch: Expression


@dataclass
class Definition(Expression):
    symbol: Symbol
    expression: Expression


@dataclass
class Application(Expression):
    invokable: Expression
    args: list[Expression]
