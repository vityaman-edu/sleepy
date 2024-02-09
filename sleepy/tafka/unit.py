from dataclasses import dataclass

from sleepy.program import ProgramUnit

from .emit import TafkaEmitVisitor
from .representation import Block, Conditional, Goto, Procedure, Return


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
        def block_text(block: Block, until: Block | None = None) -> str:
            if until is not None and block.label == until.label:
                return ""
            match block.last:
                case Goto(next):
                    return f"{block!r}\n{block_text(next, until)}"
                case Conditional(_, then_branch, else_branch, next):
                    return (
                        f"{block!r}\n"
                        f"{block_text(then_branch, until=next)}"
                        f"{block_text(else_branch, until=next)}"
                        f"{block_text(next, until)}"
                    )
                case Return():
                    return f"{block!r}\n"
                case _:
                    raise NotImplementedError

        text = ""
        for procedure in self.procedures:
            text += repr(procedure) + "\n"
            text += block_text(procedure.entry)
        text += block_text(self.main)
        return text
