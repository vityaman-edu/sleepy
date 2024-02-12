from dataclasses import dataclass

from sleepy.program import ProgramUnit

from .emit import TafkaEmitVisitor
from .representation import Block, Procedure
from .text import TafkaTextListener
from .walker import TafkaWalker


@dataclass
class TafkaUnit:
    main: Block
    procedures: list[Procedure]

    @staticmethod
    def emitted_from(unit: ProgramUnit) -> "TafkaUnit":
        tafka = TafkaEmitVisitor(unit)
        tafka.visit_program(unit.program)
        return TafkaUnit(tafka.main, tafka.procedures)

    def to_text(self) -> str:
        out = TafkaTextListener()
        walker = TafkaWalker(out)

        for procedure in self.procedures:
            walker.explore_procedure(procedure)
            out.writeln("")
        walker.explore_block(self.main)

        return out.text.getvalue()
