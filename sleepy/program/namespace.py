from abc import ABC, abstractmethod
from typing import override

from sleepy.core import SleepyError

from .representation import Symbol


class NamespaceError(SleepyError):
    pass


class DefinitionError(NamespaceError):
    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        super().__init__(f"Failed to define a name {name}: {reason}")


class NameNotFoundError(NamespaceError):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"Failed to resolve a name {name}: not found",
        )


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
