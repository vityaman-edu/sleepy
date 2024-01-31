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
    Copy,
    Div,
    Eq,
    Goto,
    Int,
    Label,
    Load,
    Lt,
    Mul,
    Rem,
    Return,
    RValue,
    Set,
    Statement,
    Sum,
    Var,
)
from sleepy.tafka.representation import Conditional as TafConditional
from sleepy.tafka.representation import Kind as TafKind

UniqueNameSequence = Generator[str, None, None]


class TafkaEmitVisitor(Visitor[None]):
    def __init__(self, unit: ProgramUnit) -> None:
        self.var_names = map(str, range(10000000))
        self.lbl_names = map(str, range(10000000))
        self.main = Block(Label("main"), [])
        self.current_block = self.main
        self.unit = unit
        self.last_result = Var("0", Int())

    @override
    def visit_program(self, tree: Program) -> None:
        for statement in tree.statements:
            self.visit_expression(statement)
        self.emit_statement(Return())

    @override
    def visit_conditional(self, tree: Conditional) -> None:
        then_block = Block(self.next_lbl(), [])
        else_block = Block(self.next_lbl(), [])
        end_block = Block(self.next_lbl(), [])

        self.visit_expression(tree.condition)
        condition = self.last_result

        br = TafConditional(condition, then_block, else_block)
        self.emit_statement(br)

        self.current_block = then_block
        self.visit_expression(tree.then_branch)
        then_result = self.last_result
        self.emit_statement(Goto(end_block))

        self.current_block = else_block
        self.visit_expression(tree.else_branch)
        self.emit_statement(Set(then_result, Copy(self.last_result)))

        self.current_block = end_block

    @override
    def visit_application(self, tree: Application) -> None:
        args = []
        for arg in tree.args:
            self.visit_expression(arg)
            args.append(self.last_result)

        symbol = cast(Symbol, tree.invokable)
        invokable = self.unit.bindings.resolve(symbol)
        match invokable:
            case Intrinsic(symbol, _, _) as intrinsic:
                match symbol.name:
                    case "sum":
                        self.emit_intermidiate(Sum(args[0], args[1]))
                    case "div":
                        self.emit_intermidiate(Div(args[0], args[1]))
                    case "rem":
                        self.emit_intermidiate(Rem(args[0], args[1]))
                    case "mul":
                        self.emit_intermidiate(Mul(args[0], args[1]))
                    case "eq":
                        self.emit_intermidiate(Eq(args[0], args[1]))
                    case "lt":
                        self.emit_intermidiate(Lt(args[0], args[1]))
                    case _:
                        raise RuntimeError(str(intrinsic))
            case _:
                raise RuntimeError(str(invokable))

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
        self.emit_intermidiate(Load(Const(str(tree.value), Int())))

    @override
    def visit_definition(self, tree: Definition) -> None:
        raise NotImplementedError

    def emit_statement(self, statement: Statement) -> None:
        if isinstance(statement, Set):
            self.last_result = statement.target
        self.current_block.statements.append(statement)

    def emit_intermidiate(self, rvalue: RValue) -> None:
        self.emit_statement(Set(self.next_var(rvalue.value), rvalue))

    def next_var(self, kind: TafKind) -> Var:
        return Var(next(self.var_names), kind)

    def next_lbl(self) -> Label:
        return Label(next(self.lbl_names))
