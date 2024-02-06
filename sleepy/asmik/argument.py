from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override


class Argument(ABC):
    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


class Register(Argument):
    @staticmethod
    def ze() -> "PhysicalRegister":
        return PhysicalRegister("ze")

    @staticmethod
    def a1() -> "PhysicalRegister":
        return PhysicalRegister("a1")

    @staticmethod
    def ra() -> "PhysicalRegister":
        return PhysicalRegister("ra")

    @staticmethod
    def ip() -> "PhysicalRegister":
        return PhysicalRegister("ip")


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
