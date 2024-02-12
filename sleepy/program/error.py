from sleepy.core import SleepyError


class SemanticError(SleepyError):
    pass


class NamespaceError(SleepyError):
    pass


class DefinitionError(NamespaceError):
    def __init__(self, name: str, reason: str) -> None:
        super().__init__(f"failed to define a name {name}: {reason}")


class NameNotFoundError(NamespaceError):
    def __init__(self, name: str) -> None:
        super().__init__(f"failed to resolve a name {name}: not found")
