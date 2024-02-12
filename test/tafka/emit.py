from test.program.parse import parse

from sleepy.tafka import TafkaUnit


def tafka_emit(source: str) -> TafkaUnit:
    unit = parse(source)
    return TafkaUnit.emitted_from(unit)
