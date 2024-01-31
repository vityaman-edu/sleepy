from dataclasses import dataclass
from typing import override

from .kind import Kind
from .node import Node


@dataclass(repr=False)
class Symbol(Node):
    name: str
    kind: Kind


@dataclass(repr=False)
class Const(Symbol):
    @override
    def __repr__(self) -> str:
        return f"const({self.name}): {self.kind}"


@dataclass(repr=False)
class Var(Symbol):
    @override
    def __repr__(self) -> str:
        return f"var({self.name}): {self.kind}"
