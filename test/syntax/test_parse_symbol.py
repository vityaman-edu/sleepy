import string

import pytest
from hypothesis import given, strategies

from sleepy.syntax import ParsingError

from .parse import parse_program


@pytest.mark.parametrize(
    ("source"),
    ["basic", "_private", "i64", "CamelCase", "snake_case", "lambda"],
)
def test_symbol_positive(source: str) -> None:
    assert parse_program(source).pythonic() == (source,)


# TODO(vityaman): fix this  # noqa: FIX002
# https://github.com/vityaman-edu/sleepy/issues/9
def test_symbol_lexing_badly() -> None:
    assert parse_program("123number").pythonic() == (123, "number")


@pytest.mark.parametrize(
    ("source"),
    ["", "css-style", '"', "sto%nks"],
)
def test_symbol_negative(source: str) -> None:
    with pytest.raises(ParsingError):
        parse_program(source)


@given(strategies.text(string.ascii_letters + "_", min_size=1))
def test_symbol_random(source: str) -> None:
    assert parse_program(source).pythonic() == (source,)
