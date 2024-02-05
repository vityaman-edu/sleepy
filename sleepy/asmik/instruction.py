from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import override

from .argument import Immediate, Integer, Register


class Instruction(ABC):
    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def action(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


@dataclass(repr=False)
class BinRegOperation(Instruction):
    result: Register
    left: Register
    right: Register

    @override
    def __repr__(self) -> str:
        return f"{self.name} {self.result}, {self.left}, {self.right}"


@dataclass(repr=False)
class Addi(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "addi"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs + rhs"


@dataclass(repr=False)
class Addim(Instruction):
    dst: Register
    lhs: Register
    rhs: Immediate

    @override
    @property
    def name(self) -> str:
        return "addim"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs + rhs"

    @override
    def __repr__(self) -> str:
        return f"{self.name} {self.dst}, {self.lhs}, {self.rhs}"


@dataclass(repr=False)
class Muli(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "muli"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs * rhs"


@dataclass(repr=False)
class Divi(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "divi"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs / rhs"


@dataclass(repr=False)
class Remi(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "remi"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs % rhs"


@dataclass(repr=False)
class Slti(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "slti"

    @override
    @property
    def action(self) -> str:
        return "dst <- (lhs < rhs) ? 1 : 0"


@dataclass(repr=False)
class Orb(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "orb"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs | rhs"


@dataclass(repr=False)
class Andb(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "andb"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs & rhs"


@dataclass(repr=False)
class Xorb(BinRegOperation):
    @override
    @property
    def name(self) -> str:
        return "xorb"

    @override
    @property
    def action(self) -> str:
        return "dst <- lhs ^ rhs"


@dataclass(repr=False)
class Load(Instruction):
    dst: Register
    src_addr: Register

    @override
    @property
    def name(self) -> str:
        return "load"

    @override
    @property
    def action(self) -> str:
        return "dst <- [src]"

    @override
    def __repr__(self) -> str:
        return f"{self.name} {self.dst}, {self.src_addr}"


@dataclass(repr=False)
class Stor(Instruction):
    dst_addr: Register
    src: Register

    @override
    @property
    def name(self) -> str:
        return "stor"

    @override
    @property
    def action(self) -> str:
        return "[dst] <- src"

    @override
    def __repr__(self) -> str:
        return f"{self.name} {self.dst_addr}, {self.src}"


@dataclass(repr=False)
class Brn(Instruction):
    cond: Register
    label: Register

    @override
    @property
    def name(self) -> str:
        return "brn"

    @override
    @property
    def action(self) -> str:
        return "ip <- (not cond) ? label : (ip + 4)"

    @override
    def __repr__(self) -> str:
        return f"{self.name} {self.cond}, {self.label}"


@dataclass(repr=False)
class Hlt(Instruction):
    @override
    @property
    def name(self) -> str:
        return "hlt"

    @override
    @property
    def action(self) -> str:
        return "halt"

    @override
    def __repr__(self) -> str:
        return f"{self.name}"


def mov(dst: Register, src: Register) -> Instruction:
    return Addim(dst, src, Integer(0))
