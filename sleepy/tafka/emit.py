from typing import override

import sleepy.tafka.representation as taf
from sleepy import program
from sleepy.core import MetaTable
from sleepy.program import ProgramUnit, ProgramVisitor


class TafkaEmitVisitor(ProgramVisitor[None]):
    def __init__(self, unit: ProgramUnit) -> None:
        self.unit = unit

        self.main = taf.Procedure(
            name="main",
            entry=taf.Block(taf.Label("main"), []),
            parameters=[],
            value=taf.Unknown(),
        )
        self.procedures: list[taf.Procedure] = []

        self.var_names = map(str, range(10000000))
        self.lbl_names = map(str, range(10000000))

        self.vars = MetaTable[taf.Var]()

        self.current_block = self.main.entry
        self.last_result = taf.Var("0", taf.Int())

    @override
    def visit_program(self, tree: program.Program) -> None:
        for statement in tree.statements:
            self.visit_expression(statement)
        self.emit_statement(taf.Return(self.last_result))
        self.main.value = self.last_result.kind

    @override
    def visit_conditional(self, tree: program.Conditional) -> None:
        then_blk = taf.Block(self.next_lbl(), [])
        else_blk = taf.Block(self.next_lbl(), [])
        next_blk = taf.Block(self.next_lbl(), [])

        self.visit_expression(tree.condition)
        condition = self.last_result

        br = taf.Conditional(condition, then_blk, else_blk, next_blk)
        self.emit_statement(br)

        self.current_block = then_blk
        self.visit_expression(tree.then_branch)
        then_result = self.last_result
        self.emit_statement(taf.Goto(next_blk))

        self.current_block = else_blk
        self.visit_expression(tree.else_branch)
        self.emit_statement(taf.Set(then_result, taf.Copy(self.last_result)))
        self.emit_statement(taf.Goto(next_blk))

        self.current_block = next_blk

    @override
    def visit_application(self, tree: program.Application) -> None:
        args = []
        for arg in tree.args:
            self.visit_expression(arg)
            args.append(self.last_result)

        match tree.invokable:
            case program.Symbol() as symbol:
                invokable = self.unit.bindings.resolve(symbol)
                match invokable:
                    case program.Intrinsic() as intrinsic:
                        self.visit_application_intrinsic(
                            intrinsic,
                            args,
                        )
                    case program.Closure() as closure:
                        self.visit_symbol(symbol)
                        self.visit_application_variable(
                            self.last_result,
                            args,
                        )
            case program.Closure() as closure:
                self.visit_lambda(closure)
                self.visit_application_variable(
                    self.last_result,
                    args,
                )

    def visit_application_intrinsic(
        self,
        intrinsic: program.Intrinsic,
        args: list[taf.Var],
    ) -> None:
        rvalue: taf.RValue
        match intrinsic.name.name:
            case "sum":
                rvalue = taf.Sum(args[0], args[1])
            case "div":
                rvalue = taf.Div(args[0], args[1])
            case "rem":
                rvalue = taf.Rem(args[0], args[1])
            case "mul":
                rvalue = taf.Mul(args[0], args[1])
            case "eq":
                rvalue = taf.Eq(args[0], args[1])
            case "lt":
                rvalue = taf.Lt(args[0], args[1])
            case "and":
                rvalue = taf.And(args[0], args[1])
            case "or":
                rvalue = taf.Or(args[0], args[1])
            case _:
                raise NotImplementedError(str(intrinsic))
        self.emit_intermidiate(rvalue)

    def visit_application_variable(
        self,
        invokable: taf.Var,
        args: list[taf.Var],
    ) -> None:
        self.emit_intermidiate(taf.Invokation(invokable, args))

    @override
    def visit_lambda(self, tree: program.Closure) -> None:
        current_block = self.current_block

        label = self.next_lbl()

        params = [
            self.next_var(taf.Kind.from_sleepy(param.kind))
            for param in tree.parameters
        ]

        for param, var in zip(tree.parameters, params, strict=True):
            self.vars[param.name] = var

        body = taf.Block(label, statements=[])

        self.current_block = body
        for statement in tree.statements:
            self.visit_expression(statement)

        self.emit_statement(taf.Return(self.last_result))

        value = self.last_result.kind

        self.current_block = current_block

        procedure = taf.Procedure(label.name, body, params, value)
        self.procedures.append(procedure)

        self.emit_intermidiate(
            taf.Load(taf.Const(label.name, procedure.signature)),
        )

    @override
    def visit_symbol(self, tree: program.Symbol) -> None:
        self.last_result = self.vars[tree]

    @override
    def visit_kind(self, tree: program.Kind) -> None:
        raise NotImplementedError

    @override
    def visit_integer(self, tree: program.Integer) -> None:
        self.emit_intermidiate(taf.Load(taf.Const(str(tree.value), taf.Int())))

    @override
    def visit_definition(self, tree: program.Definition) -> None:
        self.visit_expression(tree.expression)
        self.vars[tree.symbol] = self.last_result

    def emit_statement(self, statement: taf.Statement) -> None:
        if isinstance(statement, taf.Set):
            self.last_result = statement.target
        self.current_block.statements.append(statement)

    def emit_intermidiate(self, rvalue: taf.RValue) -> None:
        self.emit_statement(taf.Set(self.next_var(rvalue.value), rvalue))

    def next_var(self, kind: taf.Kind) -> taf.Var:
        return taf.Var(next(self.var_names), kind)

    def next_lbl(self) -> taf.Label:
        return taf.Label(next(self.lbl_names))
