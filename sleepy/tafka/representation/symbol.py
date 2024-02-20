from dataclasses import dataclass

from .kind import Kind
from .node import Node


@dataclass(repr=False, unsafe_hash=True)
class Symbol(Node):
    name: str
    kind: Kind


@dataclass(repr=False, unsafe_hash=True)
class Const(Symbol):
    def __repr__(self) -> str:
        return f"${self.name}: {self.kind}"


@dataclass(repr=False, unsafe_hash=True)
class Var(Symbol):
    def __repr__(self) -> str:
        return f"%{self.name}: {self.kind}"
