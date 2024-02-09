from test.common import parser

from sleepy.program import ProgramUnit
from sleepy.syntax import Syntax2Program


def parse(source: str) -> ProgramUnit:
    return Syntax2Program.converted(parser.parse_program(source))
