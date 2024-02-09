from test.common import parser

from sleepy.asmik import asmik_emit
from sleepy.interpreter import AsmikInterpreter
from sleepy.syntax import Syntax2Program
from sleepy.tafka import TafkaUnit


def evaluate(source: str) -> str:
    syntax = parser.parse_program(source)
    program = Syntax2Program.converted(syntax)
    tafka = TafkaUnit.emitted_from(program)
    asmik = asmik_emit(tafka)

    interp = AsmikInterpreter()
    interp.load(asmik)
    interp.run()

    return str(interp.state["registers"]["a1"])
