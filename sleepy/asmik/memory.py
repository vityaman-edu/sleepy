from typing import TYPE_CHECKING

from .data import Data

if TYPE_CHECKING:
    from .instruction import Instruction


class Memory:
    def __init__(self) -> None:
        self.stack: dict[int, Data] = {}
        self.stack_pointer = 0
        self.stack_index: dict[str, int] = {}

        self.instr: list[Instruction] = []

    def data_put(self, data: Data) -> int:
        if data.identifier not in self.stack_index:
            self.stack[self.stack_pointer] = data
            self.stack_index[data.identifier] = self.stack_pointer
            self.stack_pointer += data.size_in_bytes
        return self.stack_index[data.identifier]
