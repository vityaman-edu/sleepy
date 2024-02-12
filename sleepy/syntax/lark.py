import sys
from typing import override

from lark import (
    Lark,
    Token,
    Transformer,
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
    v_args,
)
from lark.ast_utils import create_transformer
from lark.tree import Meta

from sleepy.core import SourceLocation
from sleepy.syntax.parser import SleepyParser
from sleepy.syntax.tree import Program, _Atomic, _Expression, _Integer

from .error import ParsingError


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


class LarkParser(SleepyParser):
    GRAMMAR_FILE = "grammar.lark"
    STRATEGY = "lalr"

    AST_MODULE = "sleepy.syntax.tree"

    def __init__(self) -> None:
        self.lark = Lark.open(
            LarkParser.GRAMMAR_FILE,
            rel_to=__file__,
            parser=LarkParser.STRATEGY,
        )
        self.transformer = create_transformer(
            sys.modules[LarkParser.AST_MODULE],
            LarkToSyntaxTreeTransformer(),
        )

    @override
    def parse_program(self, source: str) -> Program:
        def location(e: UnexpectedInput) -> SourceLocation:
            return SourceLocation(e.line, e.column)

        try:
            tree = self.lark.parse(source)
            return self.transformer.transform(tree)
        except UnexpectedCharacters as e:
            message = f"found character {e.char!r}, expected {e.allowed!r}"
            raise ParsingError(message, location(e)) from e
        except UnexpectedEOF as e:
            message = f"found token <EOF>, expected {e.expected!r}"
            raise ParsingError(message, location(e)) from e
        except UnexpectedToken as e:
            rules = e.considered_rules
            message = f"found token {e.token!r}, expected {e.accepts!r}" + (
                f" considering {rules!r}" if rules is not None else ""
            )
            raise ParsingError(message, location(e)) from e
