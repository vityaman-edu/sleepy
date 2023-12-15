from sleepy.program import ProgramUnit
from sleepy.syntax import Syntax2Program, parse_program


def parse(source: str) -> ProgramUnit:
    return Syntax2Program.converted(parse_program(source))
