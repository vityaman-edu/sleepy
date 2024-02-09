import pytest

from sleepy.syntax import ParsingError, Program
from sleepy.syntax.binding import (
    define,
    func,
    if_stmt,
    integer,
    invoke,
    program,
    symbol,
)

from .parse import parse_program


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "(eq 1 1)",
            program(invoke(symbol("eq"), integer(1), integer(1))),
        ),
        (
            "(sum 1 (mul 2 p))",
            program(
                invoke(
                    symbol("sum"),
                    integer(1),
                    invoke(symbol("mul"), integer(2), symbol("p")),
                ),
            ),
        ),
        (
            "(def var 1)",
            program(
                define("var", integer(1)),
            ),
        ),
        (
            "(def inc (lambda (x int) (sum x +1)))",
            program(
                define(
                    "inc",
                    func(
                        [("x", "int")],
                        [
                            invoke(
                                symbol("sum"),
                                symbol("x"),
                                integer(1),
                            ),
                        ],
                    ),
                ),
            ),
        ),
        (
            """
(def fibb (lambda (n int)
  (if (or (eq n 0) (eq n 1))
    1
    (sum
      (self (sum n -1))
      (self (sum n -2))))))""",
            program(
                define(
                    "fibb",
                    func(
                        [("n", "int")],
                        [
                            if_stmt(
                                condition=invoke(
                                    symbol("or"),
                                    invoke(
                                        symbol("eq"),
                                        symbol("n"),
                                        integer(0),
                                    ),
                                    invoke(
                                        symbol("eq"),
                                        symbol("n"),
                                        integer(1),
                                    ),
                                ),
                                then_branch=integer(1),
                                else_branch=invoke(
                                    symbol("sum"),
                                    invoke(
                                        symbol("self"),
                                        invoke(
                                            symbol("sum"),
                                            symbol("n"),
                                            integer(-1),
                                        ),
                                    ),
                                    invoke(
                                        symbol("self"),
                                        invoke(
                                            symbol("sum"),
                                            symbol("n"),
                                            integer(-2),
                                        ),
                                    ),
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        ),
    ],
)
def test_parse_positive(source: str, expected: Program) -> None:
    actual = parse_program(source)
    assert actual.pythonic() == expected.pythonic()
    assert repr(actual) == repr(expected)
    assert actual.is_same_as(expected)


@pytest.mark.parametrize(
    ("source"),
    [
        '"',
        "(",
        ")",
        "()",
        "lol)",
        "(lambda ",
    ],
)
def test_parse_bad_braces(source: str) -> None:
    with pytest.raises(ParsingError):
        parse_program(source)


@pytest.mark.parametrize(
    ("source"),
    [
        "(lambda)",
        "(lambda 1)",
        "(lambda (x) test)",
        "(lambda (1 x) 1)",
        "(lambda (x 1) 1)",
        "(lambda (x int))",
    ],
)
def test_parse_bad_lambda(source: str) -> None:
    with pytest.raises(ParsingError):
        parse_program(source)
