from dataclasses import dataclass

from sleepy.tafka import TafkaUnit, TafkaWalker

from .argument import Integer, Unassigned
from .emit import AsmikEmitListener
from .instruction import Addim
from .memory import Memory


@dataclass
class AsmikUnit:
    memory: Memory

    @staticmethod
    def emited_from(tafka: TafkaUnit) -> "AsmikUnit":
        def resolve_addresses(asmik: AsmikEmitListener) -> None:
            for instr in asmik.memory.instr:
                if (
                    isinstance(instr, Addim)  #
                    and isinstance(instr.rhs, Unassigned)
                ):
                    label = instr.rhs.label
                    instr.rhs = Integer(asmik.resolved[label])

        asmik = AsmikEmitListener()
        walker = TafkaWalker(asmik)

        walker.explore_procedure(tafka.main)
        for proc in tafka.procedures:
            walker.explore_procedure(proc)

        resolve_addresses(asmik)

        return AsmikUnit(asmik.memory)

    def to_text(self) -> str:
        text = ""

        text += "memory stack\n"
        for addr, data in sorted(self.memory.stack.items()):
            text += f"{addr:04d}: {data!r}\n"

        text += "memory instr\n"
        for i, instruction in enumerate(self.memory.instr):
            text += f"{(i * 4):04d}: {instruction!r}\n"

        return text
