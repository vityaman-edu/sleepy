from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError
