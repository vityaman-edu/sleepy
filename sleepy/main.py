from sleepy.asmik import AsmikUnit
from sleepy.interpreter import AsmikInterpreter
from sleepy.syntax import LarkParser, to_program
from sleepy.tafka import TafkaUnit


def main() -> None:
    source = """
        (def id (lambda (n int) n))
        (def a (id 1))
        (def b (id 11))
        (def c (id 111))
        (if (and (eq a 1)
            (and (eq b 11)
                 (eq c 111))) 1 0)
    """

    parser = LarkParser()
    syntax = parser.parse_program(source)
    program = to_program(syntax)
    tafka = TafkaUnit.emitted_from(program)
    asmik = AsmikUnit.emited_from(tafka)

    interp = AsmikInterpreter()
    interp.load(asmik)
    interp.run()

    print(interp.state)  # noqa: T201
