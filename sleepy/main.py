from sleepy.asmik import asmik_emit
from sleepy.interpreter import AsmikInterpreter
from sleepy.syntax import Syntax2Program, parse_program
from sleepy.tafka import TafkaUnit


def main() -> None:
    source = """
        (if (eq 1 1) 999 666)
    """

    syntax = parse_program(source)
    program = Syntax2Program.converted(syntax)
    tafka = TafkaUnit.emitted_from(program)
    asmik = asmik_emit(tafka)

    interp = AsmikInterpreter()
    interp.load(asmik)
    interp.run()

    print(interp.state)  # noqa: T201
