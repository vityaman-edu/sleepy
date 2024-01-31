from collections.abc import Generator
from typing import cast, override

from sleepy.program import (
    Application,
    Closure,
    Conditional,
    Definition,
    Integer,
    Intrinsic,
    Kind,
    Program,
    Symbol,
    Visitor,
)
from sleepy.program.unit import ProgramUnit
from sleepy.tafka.representation import (
    Block,
    Const,
    Div,
    Int,
    Load,
    Rem,
    RValue,
    Set,
    Statement,
    Sum,
    Var,
)
from sleepy.tafka.representation import (
    Kind as TafKind,
)

UniqueNameSequence = Generator[str, None, None]


class TafkaEmitVisitor(Visitor[None]):
    def __init__(self, unit: ProgramUnit) -> None:
        self.var_names = map(str, range(10000000))
        self.top_level = Block([])
        self.unit = unit

    @override
    def visit_program(self, tree: Program) -> None:
        for statement in tree.statements:
            self.visit_expression(statement)

    @override
    def visit_conditional(self, tree: Conditional) -> None:
        raise NotImplementedError

    @override
    def visit_application(self, tree: Application) -> None:
        args = []
        for arg in tree.args:
            self.visit_expression(arg)
            args.append(self.last_result)

        rvalue: RValue
        match tree.invokable:
            case Symbol() as symbol:
                invokable = self.unit.bindings.resolve(symbol)
                match invokable:
                    case Intrinsic(
                        name=Symbol("sum"),
                        parameters=_,
                        return_kind=_,
                    ):
                        rvalue = Sum(args[0], args[1])
                    case Intrinsic(
                        name=Symbol("div"),
                        parameters=_,
                        return_kind=_,
                    ):
                        rvalue = Div(args[0], args[1])
                    case Intrinsic(
                        name=Symbol("rem"),
                        parameters=_,
                        return_kind=_,
                    ):
                        rvalue = Rem(args[0], args[1])
                    case _:
                        raise RuntimeError(str(invokable))
            case _:
                raise RuntimeError(str(tree.invokable))

        result = self.next_var(Int())
        self.emit_statement(Set(result, rvalue))

    @override
    def visit_lambda(self, tree: Closure) -> None:
        raise NotImplementedError

    @override
    def visit_symbol(self, tree: Symbol) -> None:
        raise NotImplementedError

    @override
    def visit_kind(self, tree: Kind) -> None:
        raise NotImplementedError

    @override
    def visit_integer(self, tree: Integer) -> None:
        result = self.next_var(Int())
        rvalue = Load(Const(str(tree.value), Int()))
        self.emit_statement(Set(result, rvalue))

    @override
    def visit_definition(self, tree: Definition) -> None:
        raise NotImplementedError

    def emit_statement(self, statement: Statement) -> None:
        self.top_level.statements.append(statement)

    @property
    def last_result(self) -> Var:
        return cast(Set, self.top_level.statements[-1]).target

    def next_var(self, kind: TafKind) -> Var:
        return Var(next(self.var_names), kind)
