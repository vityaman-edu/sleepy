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
    def ip() -> "PhysicalRegister":
        return PhysicalRegister("ip")

    @staticmethod
    def sp() -> "PhysicalRegister":
        return PhysicalRegister("sp")

    @staticmethod
    def ra() -> "PhysicalRegister":
        return PhysicalRegister("ra")

    @staticmethod
    def a1() -> "PhysicalRegister":
        return PhysicalRegister("a1")


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

    @staticmethod
    def arg(number: int) -> "PhysicalRegister":
        max_number = 6
        if number > max_number:
            raise NotImplementedError
        return PhysicalRegister(f"a{number}")


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
