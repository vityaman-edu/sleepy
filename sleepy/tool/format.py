from typing import override

from sleepy.program import (
    Application,
    Closure,
    Conditional,
    Definition,
    Integer,
    Kind,
    Program,
    Symbol,
    Visitor,
)


class FormatVisitor(Visitor[None]):
    def __init__(self) -> None:
        self.prefix = ""
        self.step = ""
        self.result = ""

    def step_into(self) -> None:
        self.prefix += self.step

    def step_out(self) -> None:
        self.prefix = self.prefix[: -len(self.step)]

    def write(self, text: str) -> None:
        self.result += text

    def indent(self) -> None:
        self.write(self.prefix)

    def newline(self) -> None:
        self.write(" ")

    def back(self, n: int) -> None:
        self.result = self.result[:-n]

    @override
    def visit_program(self, tree: Program) -> None:
        for statement in tree.statements:
            self.visit_expression(statement)
            self.newline()

    @override
    def visit_conditional(self, tree: Conditional) -> None:
        self.write("(if")
        self.newline()

        self.step_into()

        self.indent()
        self.visit_expression(tree.condition)
        self.newline()

        self.indent()
        self.visit_expression(tree.then_branch)
        self.newline()

        self.indent()
        self.visit_expression(tree.else_branch)
        self.write(")")

        self.step_out()

    @override
    def visit_application(self, tree: Application) -> None:
        self.write("(")
        self.visit_expression(tree.invokable)
        self.newline()

        self.step_into()

        for arg in tree.args:
            self.indent()
            self.visit_expression(arg)
            self.newline()
        if len(tree.args) != 0:
            self.back(1)

        self.step_out()

        self.write(")")

    @override
    def visit_lambda(self, tree: Closure) -> None:
        self.write("(lambda (")

        for param in tree.parameters:
            self.write(f"{param.name.name} {param.kind.name} ")
        if len(tree.parameters) != 0:
            self.back(1)

        self.write(")")

        self.step_into()

        for statement in tree.statements:
            self.newline()
            self.indent()
            self.visit_expression(statement)

        self.step_out()

        self.write(")")

    @override
    def visit_symbol(self, tree: Symbol) -> None:
        self.write(tree.name)

    @override
    def visit_kind(self, tree: Kind) -> None:
        self.write(tree.name)

    @override
    def visit_integer(self, tree: Integer) -> None:
        self.write(str(tree.value))

    @override
    def visit_definition(self, tree: Definition) -> None:
        self.write("(def ")
        self.visit_symbol(tree.symbol)
        self.write(" ")
        self.visit_expression(tree.expression)
        self.write(")")


def formatted(program: Program) -> str:
    p2f = FormatVisitor()
    p2f.visit_program(program)
    return p2f.result
