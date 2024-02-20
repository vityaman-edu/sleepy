from sleepy.asmik import AsmikUnit
from sleepy.interpreter import AsmikInterpreter
from sleepy.syntax import LarkParser, to_program
from sleepy.tafka import TafkaUnit


def main() -> None:
    source = """
    (def fibb (lambda (n int)
        (if (or (eq n 0) (eq n 1))
            1
            (sum
                (self (sum n -1))
                (self (sum n -2))))))
    (fibb 13)
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
