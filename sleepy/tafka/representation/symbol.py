from dataclasses import dataclass
from typing import override

from .kind import Kind
from .node import Node


@dataclass
class Symbol(Node):
    name: str
    kind: Kind


class Const(Symbol):
    @override
    def __repr__(self) -> str:
        return f"const({self.name}): {self.kind}"


class Var(Symbol):
    @override
    def __repr__(self) -> str:
        return f"var({self.name}): {self.kind}"
