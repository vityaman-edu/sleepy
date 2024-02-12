from dataclasses import dataclass
from typing import cast

from .kind import Kind, Signature
from .node import Node
from .rvalue import RValue
from .symbol import Const, Var


class Statement(Node):
    pass


class Jump(Statement):
    pass


@dataclass
class Return(Jump):
    value: Var


@dataclass
class Label:
    name: str


@dataclass
class Block(Node):
    label: Label
    statements: list[Statement]

    @property
    def last(self) -> Jump:
        return cast(Jump, self.statements[-1])


@dataclass
class Set(Statement):
    target: Var
    source: RValue


@dataclass
class Goto(Jump):
    block: Block


@dataclass
class Conditional(Jump):
    condition: Var
    then_branch: Block
    else_branch: Block
    next_block: Block


@dataclass
class Procedure(Node):
    name: str
    entry: Block
    parameters: list[Var]
    value: Kind

    @property
    def signature(self) -> Signature:
        return Signature(
            [_.kind for _ in self.parameters],
            self.value,
        )

    @property
    def const(self) -> Const:
        return Const(self.name, self.signature)
