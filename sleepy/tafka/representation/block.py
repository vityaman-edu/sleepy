from dataclasses import dataclass
from typing import cast, override

from .node import Node
from .rvalue import RValue
from .symbol import Var


class Statement(Node):
    pass


class Jump(Statement):
    pass


@dataclass(repr=False)
class Return(Statement):
    @override
    def __repr__(self) -> str:
        return "return"


@dataclass(repr=False)
class Label:
    name: str

    def __repr__(self) -> str:
        return f"label({self.name})"


@dataclass(repr=False)
class Block(Node):
    label: Label
    statements: list[Statement]

    @override
    def __repr__(self) -> str:
        return f"{self.label!r}:\n" + "\n".join(
            map(repr, self.statements),
        )

    @property
    def last(self) -> Jump:
        return cast(Jump, self.statements[-1])


@dataclass(repr=False)
class Set(Statement):
    target: Var
    source: RValue

    @override
    def __repr__(self) -> str:
        return f"{self.target!r} = {self.source!r}"


@dataclass(repr=False)
class Goto(Jump):
    block: Block

    @override
    def __repr__(self) -> str:
        return f"goto {self.block.label!r}"


@dataclass(repr=False)
class Conditional(Jump):
    condition: Var
    then_branch: Block
    else_branch: Block

    @property
    def end(self) -> Block:
        return cast(Goto, self.then_branch.last).block

    @override
    def __repr__(self) -> str:
        return (
            f"if {self.condition!r} "
            f"then {self.then_branch.label!r} "
            f"else {self.else_branch.label!r} "
            f"end {self.end.label!r}"
        )
