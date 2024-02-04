from collections.abc import Generator
from typing import override

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
    SymbolId,
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
    Procedure,
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
from sleepy.tafka.representation.rvalue import Invokation

UniqueNameSequence = Generator[str, None, None]


class TafkaEmitVisitor(Visitor[None]):
    def __init__(self, unit: ProgramUnit) -> None:
        self.unit = unit

        self.main = Block(Label("main"), [])

        self.var_names = map(str, range(10000000))
        self.lbl_names = map(str, range(10000000))

        self.vars: dict[SymbolId, Var] = {}
        self.procedures: list[Procedure] = []

        self.current_block = self.main
        self.last_result = Var("0", Int())

    @override
    def visit_program(self, tree: Program) -> None:
        for statement in tree.statements:
            self.visit_expression(statement)
        self.emit_intermidiate(Load(Const("0", Int())))
        self.emit_statement(Return(self.last_result))

    @override
    def visit_conditional(self, tree: Conditional) -> None:
        then_blk = Block(self.next_lbl(), [])
        else_blk = Block(self.next_lbl(), [])
        next_blk = Block(self.next_lbl(), [])

        self.visit_expression(tree.condition)
        condition = self.last_result

        br = TafConditional(condition, then_blk, else_blk, next_blk)
        self.emit_statement(br)

        self.current_block = then_blk
        self.visit_expression(tree.then_branch)
        then_result = self.last_result
        self.emit_statement(Goto(next_blk))

        self.current_block = else_blk
        self.visit_expression(tree.else_branch)
        self.emit_statement(Set(then_result, Copy(self.last_result)))
        self.emit_statement(Goto(next_blk))

        self.current_block = next_blk

    @override
    def visit_application(self, tree: Application) -> None:
        args = []
        for arg in tree.args:
            self.visit_expression(arg)
            args.append(self.last_result)

        match tree.invokable:
            case Symbol() as symbol:
                invokable = self.unit.bindings.resolve(symbol)
                match invokable:
                    case Intrinsic() as intrinsic:
                        self.visit_application_intrinsic(
                            intrinsic,
                            args,
                        )
                    case Closure() as closure:
                        self.visit_symbol(symbol)
                        self.visit_application_variable(
                            self.last_result,
                            args,
                        )
            case Closure() as closure:
                self.visit_lambda(closure)
                self.visit_application_variable(
                    self.last_result,
                    args,
                )

    def visit_application_intrinsic(
        self,
        intrinsic: Intrinsic,
        args: list[Var],
    ) -> None:
        match intrinsic.name.name:
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

    def visit_application_variable(
        self,
        invokable: Var,
        args: list[Var],
    ) -> None:
        self.emit_intermidiate(Invokation(invokable, args))

    @override
    def visit_lambda(self, tree: Closure) -> None:
        current_block = self.current_block

        label = self.next_lbl()

        params = [
            self.next_var(TafKind.from_sleepy(param.kind))
            for param in tree.parameters
        ]

        for param, var in zip(tree.parameters, params, strict=True):
            self.vars[param.name.uid] = var

        body = Block(label, statements=[])

        self.current_block = body
        for statement in tree.statements:
            self.visit_expression(statement)

        self.emit_statement(Return(self.last_result))

        value = self.last_result.kind

        self.current_block = current_block

        procedure = Procedure(label.name, body, params, value)
        self.procedures.append(procedure)

        self.emit_intermidiate(
            Load(Const(label.name, procedure.signature)),
        )

    @override
    def visit_symbol(self, tree: Symbol) -> None:
        self.last_result = self.vars[tree.uid]

    @override
    def visit_kind(self, tree: Kind) -> None:
        raise NotImplementedError

    @override
    def visit_integer(self, tree: Integer) -> None:
        self.emit_intermidiate(Load(Const(str(tree.value), Int())))

    @override
    def visit_definition(self, tree: Definition) -> None:
        self.visit_expression(tree.expression)
        self.vars[tree.symbol.uid] = self.last_result

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
