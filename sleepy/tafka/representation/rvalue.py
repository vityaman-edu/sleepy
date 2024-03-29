from abc import abstractproperty
from dataclasses import dataclass
from typing import cast, override

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


@dataclass
class Invokation(RValue):
    closure: Var
    args: list[Var]

    @override
    @property
    def value(self) -> Kind:
        return cast(Signature, self.closure.kind).value


@dataclass
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


@dataclass
class UnaryOperator(Intrinsic):
    argument: Var

    @override
    @property
    def signature(self) -> Signature:
        return Signature([self.argument.kind], self.value)

    @override
    def __repr__(self) -> str:
        return f"{self.name}({self.argument!r}): {self.value}"


@dataclass
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


@dataclass
class Copy(UnaryOperator):
    @override
    @property
    def name(self) -> str:
        return "copy"

    @override
    @property
    def value(self) -> Kind:
        return self.argument.kind


@dataclass
class Sum(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "sum"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass
class Mul(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "mul"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass
class Div(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "div"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass
class Rem(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "rem"

    @override
    @property
    def value(self) -> Kind:
        return self.left.kind


@dataclass
class Eq(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "eq"

    @override
    @property
    def value(self) -> Kind:
        return Bool()


@dataclass
class Lt(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "lt"

    @override
    @property
    def value(self) -> Kind:
        return Bool()


@dataclass
class And(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "and"

    @override
    @property
    def value(self) -> Kind:
        return Bool()


@dataclass
class Or(BinaryOperator):
    @override
    @property
    def name(self) -> str:
        return "or"

    @override
    @property
    def value(self) -> Kind:
        return Bool()
