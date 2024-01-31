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


def tafka_text(block: Block) -> str:
    match block.last:
        case Goto(next):
            return f"{block!r}\n{tafka_text(next)}"
        case Conditional(_, then_br, else_br) as cond:
            return (
                f"{block!r}\n"
                f"{then_br!r}\n"
                f"{else_br!r}\n"
                f"{tafka_text(cond.end)}"
            )
        case Return():
            return f"{block!r}\n"
        case _:
            raise NotImplementedError
