from abc import ABC, abstractmethod
from typing import override

from .exception import DefinitionError, NameNotFoundError
from .representation import Symbol


class Namespace(ABC):
    @abstractmethod
    def resolved(self, name: str) -> Symbol:
        pass

    @abstractmethod
    def define(self, symbol: Symbol) -> Symbol:
        pass

    @abstractmethod
    def fork(self) -> "Namespace":
        pass


class EpsilonNamespace(Namespace):
    @override
    def resolved(self, name: str) -> Symbol:
        raise NameNotFoundError(name)

    @override
    def define(self, symbol: Symbol) -> Symbol:
        raise DefinitionError(symbol.name, "Epsilon namespace")

    @override
    def fork(self) -> "Namespace":
        return LocalNamespace(parent=self)


class LocalNamespace(Namespace):
    def __init__(
        self,
        symbols: dict[str, Symbol] | None = None,
        parent: Namespace | None = None,
    ) -> None:
        self.symbols = symbols or {}
        self.parent = parent or EpsilonNamespace()

    @override
    def resolved(self, name: str) -> Symbol:
        return self.symbols.get(name) or self.parent.resolved(name)

    @override
    def define(self, symbol: Symbol) -> Symbol:
        self.symbols[symbol.name] = symbol
        return self.symbols[symbol.name]

    @override
    def fork(self) -> "Namespace":
        return LocalNamespace(parent=self)
