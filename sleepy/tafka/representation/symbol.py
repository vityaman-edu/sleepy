from dataclasses import dataclass

from .kind import Kind
from .node import Node


@dataclass(repr=False)
class Symbol(Node):
    name: str
    kind: Kind


@dataclass(repr=False)
class Const(Symbol):
    def __repr__(self) -> str:
        return f"${self.name}: {self.kind}"


@dataclass(repr=False)
class Var(Symbol):
    def __repr__(self) -> str:
        return f"%{self.name}: {self.kind}"
