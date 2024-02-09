from io import StringIO
from typing import override

from .representation import (
    And,
    Block,
    Conditional,
    Copy,
    Div,
    Eq,
    Goto,
    Invokation,
    Load,
    Lt,
    Mul,
    Or,
    Procedure,
    Rem,
    Return,
    Statement,
    Sum,
    Var,
)
from .walker import TafkaWalker


class TafkaTextListener(TafkaWalker.Listener):
    def __init__(self) -> None:
        self.text = StringIO()
        self.indent = 0

    def write(self, text: str) -> None:
        self.text.write(text)

    def writeln(self, line: str) -> None:
        self.write(f"{'  ' * self.indent}{line}\n")

    @override
    def enter_procedure(self, procedure: Procedure) -> None:
        self.writeln(
            f"procedure @{procedure.name}("
            f"{', '.join(map(repr, procedure.parameters))}) "
            f"-> {procedure.value!r} {'{'}",
        )

    @override
    def exit_procedure(self, procedure: Procedure) -> None:
        self.writeln("}")

    @override
    def enter_block(self, block: Block) -> None:
        self.writeln(f"{block.label.name}:")
        self.indent += 1

    @override
    def exit_block(self, block: Block) -> None:
        self.indent -= 1

    @override
    def enter_statement(self, statement: Statement) -> None:
        pass

    @override
    def exit_statement(self, statement: Statement) -> None:
        pass

    @override
    def on_return(self, ret: Return) -> None:
        self.writeln(f"return {ret.value}")

    @override
    def on_goto(self, goto: Goto) -> None:
        self.writeln(f"goto {goto.block.label.name}")

    @override
    def on_conditional(self, conditional: Conditional) -> None:
        self.writeln(
            f"if {conditional.condition!r} "
            f"then {conditional.then_branch.label.name} "
            f"else {conditional.else_branch.label.name} "
            f"next {conditional.next_block.label.name}",
        )

    @override
    def on_invokation(self, target: Var, source: Invokation) -> None:
        self.writeln(
            f"{target!r} = invoke @{source.closure.name}"
            f" {', '.join(map(repr, source.args))}",
        )

    @override
    def on_load(self, target: Var, source: Load) -> None:
        self.writeln(f"{target!r} = load {source.constant!r}")

    @override
    def on_copy(self, target: Var, source: Copy) -> None:
        self.writeln(f"{target!r} = copy {source.argument!r}")

    @override
    def on_sum(self, target: Var, source: Sum) -> None:
        self.writeln(f"{target!r} = sum {source.left!r}, {source.right!r}")

    @override
    def on_mul(self, target: Var, source: Mul) -> None:
        self.writeln(f"{target!r} = mul {source.left!r}, {source.right!r}")

    @override
    def on_div(self, target: Var, source: Div) -> None:
        self.writeln(f"{target!r} = div {source.left!r}, {source.right!r}")

    @override
    def on_rem(self, target: Var, source: Rem) -> None:
        self.writeln(f"{target!r} = rem {source.left!r}, {source.right!r}")

    @override
    def on_eq(self, target: Var, source: Eq) -> None:
        self.writeln(f"{target!r} = eq {source.left!r}, {source.right!r}")

    @override
    def on_lt(self, target: Var, source: Lt) -> None:
        self.writeln(f"{target!r} = lt {source.left!r}, {source.right!r}")

    @override
    def on_and(self, target: Var, source: And) -> None:
        self.writeln(f"{target!r} = and {source.left!r}, {source.right!r}")

    @override
    def on_or(self, target: Var, source: Or) -> None:
        self.writeln(f"{target!r} = or {source.left!r}, {source.right!r}")
