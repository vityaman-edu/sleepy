from abc import abstractproperty
from dataclasses import dataclass
from typing import override

from .kind import Bool, Kind, Signature
from .node import Node
from .symbol import Const, Var


class RValue(Node):
    @abstractproperty
    def value(self) -> Kind:
        raise NotImplementedError


class Intrinsic(RValue):
    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def signature(self) -> Signature:
        raise NotImplementedError


@dataclass(repr=False)
class Load(Intrinsic):
    constant: Const

    @override
    @property
    def name(self) -> str:
        return "load"

    @override
    @property
    def value(self) -> Kind:
        return self.constant.kind

    @override
    @property
    def signature(self) -> Signature:
        return Signature([self.constant.kind], self.value)

    @override
    def __repr__(self) -> str:
        return f"{self.name}({self.constant!r}): {self.value}"


@dataclass(repr=False)
class UnaryOperator(Intrinsic):
    argument: Var

    @override
    @property
    def signature(self) -> Signature:
        return Signature([self.argument.kind], self.value)

    @override
    def __repr__(self) -> str:
        return f"{self.name}({self.argument!r}): {self.value}"


@dataclass(repr=False)
class BinaryOperator(Intrinsic):
    left: Var
    right: Var

    @override
    @property
    def signature(self) -> Signature:
        return Signature(
            [self.left.kind, self.right.kind],
            self.value,
        )

    @override
    def __repr__(self) -> str:
        return (
            f"{self.name}({self.left!r}, {self.right!r}): "
            f"{self.value}"
        )


@dataclass(repr=False)
class Copy(UnaryOperator):
    @override
    @property
    def name(self) -> str:
        return "copy"

    @override
    @property
    def value(self) -> Kind:
        return self.argument.kind


@dataclass(repr=False)
class Sum(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "sum"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass(repr=False)
class Mul(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "mul"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass(repr=False)
class Div(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "div"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass(repr=False)
class Rem(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "rem"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass(repr=False)
class Eq(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "eq"

    @override
    @property
    def value(self) -> Kind:
        return Bool()


@dataclass(repr=False)
class Lt(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "lt"

    @override
    @property
    def value(self) -> Kind:
        return Bool()
