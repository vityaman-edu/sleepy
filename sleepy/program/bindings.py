from abc import ABC, abstractmethod
from typing import override

from .representation import Expression, Symbol


class Bindings(ABC):
    @abstractmethod
    def bind(self, symbol: Symbol, expression: Expression) -> None:
        pass

    @abstractmethod
    def resolve(self, symbol: Symbol) -> Expression:
        pass


class BasicBindings(Bindings):
    def __init__(
        self,
        expressions: dict[int, Expression] | None = None,
    ) -> None:
        self.expressions = expressions or {}

    @override
    def bind(self, symbol: Symbol, expression: Expression) -> None:
        self.expressions[symbol.uid] = expression

    @override
    def resolve(self, symbol: Symbol) -> Expression:
        return self.expressions[symbol.uid]
