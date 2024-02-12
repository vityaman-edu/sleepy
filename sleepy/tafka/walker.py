from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from .representation import (
    And,
    Block,
    Conditional,
    Copy,
    Div,
    Eq,
    Goto,
    Intrinsic,
    Invokation,
    Jump,
    Load,
    Lt,
    Mul,
    Or,
    Procedure,
    Rem,
    Return,
    Set,
    Statement,
    Sum,
    Var,
)


@dataclass
class Context:
    position: int
    block: Block


class TafkaWalker:
    class Listener(ABC):
        @abstractmethod
        def enter_procedure(self, procedure: Procedure) -> None:
            raise NotImplementedError

        @abstractmethod
        def exit_procedure(self, procedure: Procedure) -> None:
            raise NotImplementedError

        @abstractmethod
        def enter_block(self, block: Block) -> None:
            raise NotImplementedError

        @abstractmethod
        def exit_block(self, block: Block) -> None:
            raise NotImplementedError

        @abstractmethod
        def enter_statement(self, statement: Statement) -> None:
            raise NotImplementedError

        @abstractmethod
        def exit_statement(self, statement: Statement) -> None:
            raise NotImplementedError

        def on_statement(self, statement: Statement) -> None:
            self.enter_statement(statement)
            match statement:
                case Jump() as jump:
                    self.on_jump(jump)
                case Set() as statement:
                    self.on_assignment(statement)
                case _:
                    raise NotImplementedError
            self.exit_statement(statement)

        def on_jump(self, jump: Jump) -> None:
            match jump:
                case Return() as ret:
                    self.on_return(ret)
                case Goto() as goto:
                    self.on_goto(goto)
                case Conditional() as conditional:
                    self.on_conditional(conditional)
                case _:
                    raise NotImplementedError

        def on_assignment(self, assignment: Set) -> None:
            match assignment.source:
                case Intrinsic() as source:
                    self.on_instrinsic(assignment.target, source)
                case Invokation() as source:
                    self.on_invokation(assignment.target, source)
                case _:
                    raise NotImplementedError

        def on_instrinsic(self, target: Var, source: Intrinsic) -> None:
            match source:
                case Load():
                    self.on_load(target, source)
                case Copy():
                    self.on_copy(target, source)
                case Sum():
                    self.on_sum(target, source)
                case Mul():
                    self.on_mul(target, source)
                case Div():
                    self.on_div(target, source)
                case Rem():
                    self.on_rem(target, source)
                case Eq():
                    self.on_eq(target, source)
                case Lt():
                    self.on_lt(target, source)
                case And():
                    self.on_and(target, source)
                case Or():
                    self.on_or(target, source)
                case _:
                    raise NotImplementedError

        @abstractmethod
        def on_return(self, ret: Return) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_goto(self, goto: Goto) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_conditional(self, conditional: Conditional) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_invokation(self, target: Var, source: Invokation) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_load(self, target: Var, source: Load) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_copy(self, target: Var, source: Copy) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_sum(self, target: Var, source: Sum) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_mul(self, target: Var, source: Mul) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_div(self, target: Var, source: Div) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_rem(self, target: Var, source: Rem) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_eq(self, target: Var, source: Eq) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_lt(self, target: Var, source: Lt) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_and(self, target: Var, source: And) -> None:
            raise NotImplementedError

        @abstractmethod
        def on_or(self, target: Var, source: Or) -> None:
            raise NotImplementedError

    class ContextedListener(Listener):
        def __init__(self) -> None:
            super().__init__()
            self.position = 0
            self.block: Block

        @override
        def enter_block(self, block: Block) -> None:
            self.block = block

        @override
        def enter_statement(self, statement: Statement) -> None:
            self.position += 1

        @property
        def context(self) -> Context:
            return Context(self.position, self.block)

    def __init__(self, listener: Listener) -> None:
        self.listener = listener

    def explore_procedure(self, procedure: Procedure) -> None:
        self.listener.enter_procedure(procedure)
        self.explore_block(procedure.entry)
        self.listener.exit_procedure(procedure)

    def explore_block(self, block: Block, until: Block | None = None) -> None:
        if until is not None and block.label == until.label:
            return

        self.listener.enter_block(block)
        for statement in block.statements:
            self.listener.on_statement(statement)
        self.listener.exit_block(block)

        match block.last:
            case Goto(next):
                self.explore_block(next, until)
            case Conditional(_, then_branch, else_branch, next):
                self.explore_block(then_branch, until=next)
                self.explore_block(else_branch, until=next)
                self.explore_block(next, until)
            case Return():
                pass
            case _:
                raise NotImplementedError
