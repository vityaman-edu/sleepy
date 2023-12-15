from dataclasses import dataclass
from typing import NamedTuple


class ProgramNode:
    @property
    def uid(self) -> int:
        return id(self)


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


class Kind(ProgramNode):
    name: str


@dataclass
class Lambda(Expression):
    class Parameter(NamedTuple):
        name: Symbol
        kind: Kind

    parameters: list[Parameter]
    statements: list[Expression]


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
