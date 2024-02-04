from sleepy.tafka.emit import TafkaEmitVisitor
from sleepy.tafka.representation import (
    Block,
    Conditional,
    Goto,
    Return,
)


def tafka_text(tafka: TafkaEmitVisitor) -> str:
    text = ""

    for procedure in tafka.procedures:
        text += repr(procedure) + "\n"
        text += tafka_block_text(procedure.entry)

    text += tafka_block_text(tafka.main)

    return text


def tafka_block_text(block: Block, until: Block | None = None) -> str:
    if until is not None and block.label == until.label:
        return ""

    match block.last:
        case Goto(next):
            return f"{block!r}\n{tafka_block_text(next, until)}"
        case Conditional(_, then_br, else_br) as cond:
            return (
                f"{block!r}\n"
                f"{tafka_block_text(then_br, until=cond.next_block)}"
                f"{tafka_block_text(else_br, until=cond.next_block)}"
                f"{tafka_block_text(cond.next_block, until)}"
            )
        case Return():
            return f"{block!r}\n"
        case _:
            raise NotImplementedError
