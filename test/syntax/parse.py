from test.common import parser

from sleepy.syntax import Program


def parse_program(source: str) -> Program:
    return parser.parse_program(source)
