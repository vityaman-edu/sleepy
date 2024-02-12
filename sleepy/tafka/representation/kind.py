from dataclasses import dataclass
from typing import override

from sleepy.program.representation import Kind as SleepyKind

from .node import Node


class Kind(Node):
    @classmethod
    def from_sleepy(cls, kind: SleepyKind) -> "Kind":
        match kind.name:
            case "int":
                return Int()
            case "bool":
                return Bool()
            case _:
                raise NotImplementedError


@dataclass(repr=False)
class Unknown(Kind):
    @override
    def __repr__(self) -> str:
        return "?"


@dataclass(repr=False)
class Int(Kind):
    @override
    def __repr__(self) -> str:
        return "int"


@dataclass(repr=False)
class Bool(Kind):
    @override
    def __repr__(self) -> str:
        return "bool"


@dataclass(repr=False)
class Signature(Kind):
    params: list[Kind]
    value: Kind

    @override
    def __repr__(self) -> str:
        return f"({', '.join(repr(_) for _ in self.params)}) -> {self.value!r}"
