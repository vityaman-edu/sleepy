from test.program.parse import parse

from sleepy.tafka.emit import TafkaEmitVisitor
from sleepy.tafka.representation import (
    Block,
    Conditional,
    Goto,
    Return,
)


def tafka_emit(source: str) -> TafkaEmitVisitor:
    unit = parse(source)

    tafka = TafkaEmitVisitor(unit)
    tafka.visit_program(unit.program)

    return tafka


def tafka_text(block: Block, until: Block | None = None) -> str:
    if until is not None and block.label == until.label:
        return ""

    match block.last:
        case Goto(next):
            return f"{block!r}\n{tafka_text(next, until)}"
        case Conditional(_, then_br, else_br) as cond:
            return (
                f"{block!r}\n"
                f"{tafka_text(then_br, until=cond.next_block)}"
                f"{tafka_text(else_br, until=cond.next_block)}"
                f"{tafka_text(cond.next_block, until)}"
            )
        case Return():
            return f"{block!r}\n"
        case _:
            raise NotImplementedError
