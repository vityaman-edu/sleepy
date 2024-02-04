from test.program.parse import parse

from sleepy.tafka.emit import TafkaEmitVisitor


def tafka_emit(source: str) -> TafkaEmitVisitor:
    unit = parse(source)

    tafka = TafkaEmitVisitor(unit)
    tafka.visit_program(unit.program)

    return tafka
