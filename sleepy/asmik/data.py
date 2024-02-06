from abc import ABC, abstractmethod, abstractproperty
from typing import override


class Data(ABC):
    @abstractproperty
    def size_in_bytes(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @property
    def identifier(self) -> str:
        return repr(self)


class IntegerData(Data):
    def __init__(self, value: int) -> None:
        self.value = value

    @override
    @property
    def size_in_bytes(self) -> int:
        return 8

    @override
    def __repr__(self) -> str:
        return f"{self.value} # const({self.value}): int"
