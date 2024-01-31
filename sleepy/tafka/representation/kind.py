from dataclasses import dataclass
from typing import override

from .node import Node


class Kind(Node):
    pass


@dataclass(repr=False)
class Int(Kind):
    @override
    def __repr__(self) -> str:
        return "int"


@dataclass(repr=False)
class Signature(Kind):
    params: list[Kind]
    value: Kind

    @override
    def __repr__(self) -> str:
        return (
            f"({', '.join(repr(_) for _ in self.params)}) "
            f"-> {self.value!r}"
        )
