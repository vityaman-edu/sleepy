import sys
from abc import ABC
from dataclasses import dataclass, field

from lark import Lark, Token, Transformer, v_args
from lark.ast_utils import AsList, Ast, WithMeta, create_transformer
from lark.exceptions import LexError, ParseError
from lark.tree import Meta

from .exception import SleepySyntaxError

PythonRepr = int | str | tuple


class _SyntaxTree(ABC, Ast):
    def pythonic(self) -> PythonRepr:
        raise NotImplementedError

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        raise NotImplementedError


class _Expression(_SyntaxTree):
    pass


class _Atomic(_Expression):
    pass


@dataclass
class Program(_SyntaxTree, AsList, WithMeta):
    meta: Meta = field(repr=False)
    expressions: list[_Expression]

    def pythonic(self) -> PythonRepr:
        return tuple(e.pythonic() for e in self.expressions)

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, Program) and all(
            this.is_same_as(that)
            for this, that in zip(
                self.expressions,
                other.expressions,
                strict=True,
            )
        )


@dataclass
class Symbol(_Atomic, WithMeta):
    meta: Meta = field(repr=False)
    name: str

    def pythonic(self) -> PythonRepr:
        return self.name

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, Symbol) and self.name == other.name


@dataclass
class _Integer(_Atomic, WithMeta):
    meta: Meta = field(repr=False)
    value: int

    def pythonic(self) -> PythonRepr:
        return self.value

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return (
            isinstance(other, _Integer) and self.value == other.value
        )


@dataclass
class String(_Atomic, WithMeta):
    meta: Meta = field(repr=False)
    value: str

    def pythonic(self) -> PythonRepr:
        return self.value

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, String) and self.value == other.value


@dataclass
class Kind(_SyntaxTree, WithMeta):
    meta: Meta = field(repr=False)
    name: Symbol

    def pythonic(self) -> PythonRepr:
        return self.name.pythonic()

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, Kind) and self.name.is_same_as(
            other.name,
        )


@dataclass
class Parameter(_SyntaxTree, WithMeta):
    meta: Meta = field(repr=False)
    symbol: Symbol
    kind: Kind

    def pythonic(self) -> PythonRepr:
        return (self.kind.pythonic(), self.kind.pythonic())

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return (
            isinstance(other, Parameter)
            and self.symbol.is_same_as(other.symbol)
            and self.kind.is_same_as(other.kind)
        )


@dataclass
class Parameters(_SyntaxTree, AsList, WithMeta):
    meta: Meta = field(repr=False)
    parameters: list[Parameter]

    def pythonic(self) -> tuple:
        return tuple(e.pythonic() for e in self.parameters)

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, Parameters) and all(
            this.is_same_as(that)
            for this, that in zip(
                self.parameters,
                other.parameters,
                strict=True,
            )
        )


@dataclass
class Body(_SyntaxTree, AsList, WithMeta):
    meta: Meta = field(repr=False)
    expressions: list[_Expression]

    def pythonic(self) -> tuple:
        return tuple(e.pythonic() for e in self.expressions)

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, Body) and all(
            this.is_same_as(that)
            for this, that in zip(
                self.expressions,
                other.expressions,
                strict=True,
            )
        )


@dataclass
class Lambda(_Expression, WithMeta):
    meta: Meta = field(repr=False)
    parameters: Parameters
    body: Body

    def pythonic(self) -> PythonRepr:
        return (
            "lambda",
            self.parameters.pythonic(),
            *self.body.pythonic(),
        )

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return (
            isinstance(other, Lambda)
            and self.parameters.is_same_as(other.parameters)
            and self.body.is_same_as(other.body)
        )


@dataclass
class Condition(_SyntaxTree, WithMeta):
    meta: Meta = field(repr=False)
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(
            other,
            Condition,
        ) and self.expression.is_same_as(other.expression)


@dataclass
class ThenBranch(_SyntaxTree, WithMeta):
    meta: Meta = field(repr=False)
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(
            other,
            ThenBranch,
        ) and self.expression.is_same_as(other.expression)


@dataclass
class ElseBranch(_SyntaxTree, WithMeta):
    meta: Meta = field(repr=False)
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(
            other,
            ElseBranch,
        ) and self.expression.is_same_as(other.expression)


@dataclass
class IfExpression(_Expression, WithMeta):
    meta: Meta = field(repr=False)
    condition: Condition
    then_branch: ThenBranch
    else_branch: ElseBranch

    def pythonic(self) -> tuple:
        return (
            "if",
            self.condition.pythonic(),
            self.then_branch.pythonic(),
            self.else_branch.pythonic(),
        )

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return (
            isinstance(other, IfExpression)
            and self.condition.is_same_as(other.condition)
            and self.then_branch.is_same_as(other.then_branch)
            and self.else_branch.is_same_as(other.else_branch)
        )


@dataclass
class VariableDefinition(_Expression, WithMeta):
    meta: Meta = field(repr=False)
    symbol: Symbol
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return (
            "def",
            self.symbol.pythonic(),
            self.expression.pythonic(),
        )

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return (
            isinstance(other, VariableDefinition)
            and self.symbol.is_same_as(other.symbol)
            and self.expression.is_same_as(other.expression)
        )


@dataclass
class Invokable(_SyntaxTree, WithMeta):
    meta: Meta = field(repr=False)
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(
            other,
            Invokable,
        ) and self.expression.is_same_as(other.expression)


@dataclass
class Args(_SyntaxTree, AsList, WithMeta):
    meta: Meta = field(repr=False)
    expressions: list[_Expression]

    def pythonic(self) -> tuple:
        return tuple(e.pythonic() for e in self.expressions)

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return isinstance(other, Args) and all(
            this.is_same_as(that)
            for this, that in zip(
                self.expressions,
                other.expressions,
                strict=True,
            )
        )


@dataclass
class Application(_Expression, WithMeta):
    meta: Meta = field(repr=False)
    invokable: Invokable
    args: Args

    def pythonic(self) -> tuple:
        return (self.invokable.pythonic(), *self.args.pythonic())

    def is_same_as(self, other: "_SyntaxTree") -> bool:
        return (
            isinstance(other, Application)
            and self.invokable.is_same_as(other.invokable)
            and self.args.is_same_as(other.args)
        )


class LarkToSyntaxTreeTransformer(Transformer):
    def NAME(self, token: Token) -> str:  # noqa: N802
        return token.value

    def STRING(self, token: Token) -> str:  # noqa: N802
        return token.value[1:-1]

    @v_args(meta=True)
    def integer(self, meta: Meta, tokens: list[Token]) -> _Integer:
        if len(tokens) == 1:
            tokens.insert(0, Token("SIGN", "+"))

        sign = -1 if tokens[0].value == "-" else 1
        number = int(tokens[1].value)

        return _Integer(meta, sign * number)

    @v_args(inline=True)
    def expression(self, tree: _Expression) -> _Expression:
        return tree

    @v_args(inline=True)
    def atomic(self, tree: _Atomic) -> _Atomic:
        return tree

    @v_args(inline=True)
    def start(self, tree: Program) -> Program:
        return tree


parser = Lark.open("grammar.lark", rel_to=__file__, parser="lalr")

transformer = create_transformer(
    sys.modules[__name__],
    LarkToSyntaxTreeTransformer(),
)


def parse_program(text: str) -> _SyntaxTree:
    try:
        tree = parser.parse(text)
    except ParseError as e:
        raise SleepySyntaxError from e
    except LexError as e:
        raise SleepySyntaxError from e

    return transformer.transform(tree)
