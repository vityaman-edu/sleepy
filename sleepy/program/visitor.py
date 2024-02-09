from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .representation import (
    Application,
    Closure,
    Conditional,
    Definition,
    Expression,
    Integer,
    Kind,
    Program,
    Symbol,
)

T = TypeVar("T")


class ProgramVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_program(self, tree: Program) -> T:
        pass

    @abstractmethod
    def visit_conditional(self, tree: Conditional) -> T:
        pass

    @abstractmethod
    def visit_application(self, tree: Application) -> T:
        pass

    @abstractmethod
    def visit_lambda(self, tree: Closure) -> T:
        pass

    @abstractmethod
    def visit_symbol(self, tree: Symbol) -> T:
        pass

    @abstractmethod
    def visit_kind(self, tree: Kind) -> T:
        pass

    @abstractmethod
    def visit_integer(self, tree: Integer) -> T:
        pass

    @abstractmethod
    def visit_definition(self, tree: Definition) -> T:
        pass

    def visit_expression(self, expression: Expression) -> T:
        match expression:
            case Application() as expression:
                return self.visit_application(expression)
            case Conditional() as expression:
                return self.visit_conditional(expression)
            case Closure() as expression:
                return self.visit_lambda(expression)
            case Symbol() as expression:
                return self.visit_symbol(expression)
            case Integer() as expression:
                return self.visit_integer(expression)
            case Definition() as expression:
                return self.visit_definition(expression)
        raise NotImplementedError
