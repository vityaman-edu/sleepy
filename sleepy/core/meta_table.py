from abc import ABC, abstractproperty
from typing import Generic, NewType, TypeVar

UID = NewType("UID", int)

T = TypeVar("T")


class Identifiable(ABC):
    @abstractproperty
    def uid(self) -> UID:
        raise NotImplementedError


class MetaTable(Generic[T]):
    def __init__(self) -> None:
        self.entries: dict[UID, T] = {}

    def __getitem__(self, key: Identifiable) -> T:
        try:
            return self.entries[key.uid]
        except KeyError as e:
            e.add_note(f"key: {key!r}")
            raise

    def __setitem__(self, key: Identifiable, value: T) -> None:
        if key.uid in self.entries:
            message = f"can't assign {value}, to key with id {key.uid}: {key!r}"
            raise KeyError(message)
        self.entries[key.uid] = value
