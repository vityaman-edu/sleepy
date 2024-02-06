from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override


class Argument(ABC):
    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


class Register(Argument):
    @classmethod
    def ze(cls) -> "PhysicalRegister":
        return PhysicalRegister("ze")

    @classmethod
    def a1(cls) -> "PhysicalRegister":
        return PhysicalRegister("a1")

    @classmethod
    def ra(cls) -> "PhysicalRegister":
        return PhysicalRegister("ra")


@dataclass(repr=False)
class VirtualRegister(Register):
    number: int

    @override
    def __repr__(self) -> str:
        return f"v{self.number}"


@dataclass(repr=False)
class PhysicalRegister(Register):
    name: str

    @override
    def __repr__(self) -> str:
        return self.name


class Immediate(Argument):
    pass


@dataclass(repr=False)
class Integer(Immediate):
    value: int

    @override
    def __repr__(self) -> str:
        return f"{self.value}"


@dataclass(repr=False)
class Unassigned(Immediate):
    label: str

    @override
    def __repr__(self) -> str:
        return f"<{self.label}>"
