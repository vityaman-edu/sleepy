from dataclasses import dataclass
from typing import cast, override

from .kind import Kind, Signature
from .node import Node
from .rvalue import RValue
from .symbol import Const, Var


class Statement(Node):
    pass


class Jump(Statement):
    pass


@dataclass(repr=False)
class Return(Jump):
    value: Var

    @override
    def __repr__(self) -> str:
        return f"return {self.value}"


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
    next_block: Block

    @override
    def __repr__(self) -> str:
        return (
            f"if {self.condition!r} "
            f"then {self.then_branch.label!r} "
            f"else {self.else_branch.label!r} "
            f"end {self.next_block.label!r}"
        )


@dataclass(repr=False)
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

    @override
    def __repr__(self) -> str:
        return (
            f"procedure {self.name}("
            f"{', '.join(map(repr, self.parameters))}) "
            f"-> {self.value!r}"
        )
