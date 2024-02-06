import json

from sleepy.asmik import asmik_emit
from sleepy.interpreter import AsmikInterpreter
from sleepy.syntax import Syntax2Program, parse_program
from sleepy.tafka import TafkaUnit


def main() -> None:
    source = """
        (sum (div 5 2) (rem (sum 2 2) 2))
    """

    syntax = parse_program(source)
    program = Syntax2Program.converted(syntax)
    tafka = TafkaUnit.emitted_from(program)
    asmik = asmik_emit(tafka)

    interp = AsmikInterpreter()
    interp.load(asmik)
    interp.run()

    print(json.dumps(interp.state, indent=2))  # noqa: T201
