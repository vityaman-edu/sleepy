from dataclasses import dataclass
from typing import override

from .node import Node
from .rvalue import RValue
from .symbol import Var


class Statement(Node):
    pass


@dataclass
class Set(Statement):
    target: Var
    source: RValue

    @override
    def __repr__(self) -> str:
        return f"{self.target!r} = {self.source!r}"


@dataclass
class Block(Node):
    statements: list[Statement]

    @override
    def __repr__(self) -> str:
        return "\n".join(map(repr, self.statements))
