from test.common import parser

from sleepy.program import ProgramUnit
from sleepy.syntax import to_program


def parse(source: str) -> ProgramUnit:
    return to_program(parser.parse_program(source))
