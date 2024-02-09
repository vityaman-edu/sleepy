from abc import ABC, abstractmethod

from sleepy.syntax.tree import Program


class SleepyParser(ABC):
    @abstractmethod
    def parse_program(self, source: str) -> Program:
        raise NotImplementedError
