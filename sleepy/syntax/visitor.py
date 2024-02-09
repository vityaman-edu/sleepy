from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .tree import (
    Application,
    IfExpression,
    Kind,
    Lambda,
    Program,
    Symbol,
    VariableDefinition,
)
from .tree import _Expression as Expression
from .tree import _Integer as Integer

T = TypeVar("T")


class Visitor(ABC, Generic[T]):
    @abstractmethod
    def visit_program(self, tree: Program) -> T:
        pass

    @abstractmethod
    def visit_conditional(self, tree: IfExpression) -> T:
        pass

    @abstractmethod
    def visit_application(self, tree: Application) -> T:
        pass

    @abstractmethod
    def visit_lambda(self, tree: Lambda) -> T:
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
    def visit_definition(self, tree: VariableDefinition) -> T:
        pass

    def visit_expression(self, expression: Expression) -> T:
        match expression:
            case Application() as expression:
                return self.visit_application(expression)
            case IfExpression() as expression:
                return self.visit_conditional(expression)
            case Lambda() as expression:
                return self.visit_lambda(expression)
            case Symbol() as expression:
                return self.visit_symbol(expression)
            case Integer() as expression:
                return self.visit_integer(expression)
            case VariableDefinition() as expression:
                return self.visit_definition(expression)
        raise NotImplementedError
