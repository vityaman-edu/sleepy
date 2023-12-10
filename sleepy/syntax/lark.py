import sys
from abc import ABC
from dataclasses import dataclass

from lark import Lark, Token, Transformer, v_args
from lark.ast_utils import AsList, Ast, WithMeta, create_transformer
from lark.exceptions import LexError, ParseError
from lark.tree import Meta

from .exception import SleepySyntaxError

PythonRepr = int | str | tuple


class _SyntaxTree(ABC, Ast):
    def pythonic(self) -> PythonRepr:
        raise NotImplementedError


class _Expression(_SyntaxTree):
    pass


class _Atomic(_Expression):
    pass


@dataclass
class Program(_SyntaxTree, AsList, WithMeta):
    meta: Meta
    expressions: list[_Expression]

    def pythonic(self) -> PythonRepr:
        return tuple(e.pythonic() for e in self.expressions)


@dataclass
class Symbol(_Atomic, WithMeta):
    meta: Meta
    name: str

    def pythonic(self) -> PythonRepr:
        return self.name


@dataclass
class _Integer(_Atomic, WithMeta):
    meta: Meta
    value: int

    def pythonic(self) -> PythonRepr:
        return self.value


@dataclass
class String(_Atomic, WithMeta):
    meta: Meta
    value: str

    def pythonic(self) -> PythonRepr:
        return self.value


@dataclass
class Kind(_SyntaxTree, WithMeta):
    meta: Meta
    name: Symbol

    def pythonic(self) -> PythonRepr:
        return self.name.pythonic()


@dataclass
class Parameter(_SyntaxTree, WithMeta):
    meta: Meta
    symbol: Symbol
    kind: Kind

    def pythonic(self) -> PythonRepr:
        return (self.kind.pythonic(), self.kind.pythonic())


@dataclass
class Parameters(_SyntaxTree, AsList, WithMeta):
    meta: Meta
    parameters: list[Parameter]

    def pythonic(self) -> tuple:
        return tuple(e.pythonic() for e in self.parameters)


@dataclass
class Body(_SyntaxTree, AsList, WithMeta):
    meta: Meta
    expressions: list[_Expression]

    def pythonic(self) -> tuple:
        return tuple(e.pythonic() for e in self.expressions)


@dataclass
class Lambda(_Expression, WithMeta):
    meta: Meta
    parameters: Parameters
    body: Body

    def pythonic(self) -> PythonRepr:
        return (
            "lambda",
            self.parameters.pythonic(),
            *self.body.pythonic(),
        )


@dataclass
class Condition(_SyntaxTree, WithMeta):
    meta: Meta
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()


@dataclass
class ThenBranch(_SyntaxTree, WithMeta):
    meta: Meta
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()


@dataclass
class ElseBranch(_SyntaxTree, WithMeta):
    meta: Meta
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()


@dataclass
class IfExpression(_Expression, WithMeta):
    meta: Meta
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


@dataclass
class VariableDefinition(_Expression, WithMeta):
    meta: Meta
    symbol: Symbol
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return (
            "def",
            self.symbol.pythonic(),
            self.expression.pythonic(),
        )


@dataclass
class Invokable(_SyntaxTree, WithMeta):
    meta: Meta
    expression: _Expression

    def pythonic(self) -> PythonRepr:
        return self.expression.pythonic()


@dataclass
class Args(_SyntaxTree, AsList, WithMeta):
    meta: Meta
    expressions: list[_Expression]

    def pythonic(self) -> tuple:
        return tuple(e.pythonic() for e in self.expressions)


@dataclass
class Application(_Expression, WithMeta):
    meta: Meta
    invokable: Invokable
    args: Args

    def pythonic(self) -> tuple:
        return (self.invokable.pythonic(), *self.args.pythonic())


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
