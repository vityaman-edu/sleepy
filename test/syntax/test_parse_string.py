import string

import pytest
from hypothesis import given, strategies

from sleepy.syntax import SleepySyntaxError, parse_program


@pytest.mark.parametrize(
    ("source"),
    ["''", '""', "'single-quoted!'", '"double-quoted?"'],
)
def test_string_positive(source: str) -> None:
    assert parse_program(source).pythonic() == (source[1:-1],)


@pytest.mark.parametrize(
    ("source"),
    ['"', 'forgot left"', '"forgot right', "\n"],
)
def test_string_negative(source: str) -> None:
    with pytest.raises(SleepySyntaxError):
        parse_program(source)


@given(
    strategies.text(
        string.digits
        + string.ascii_letters
        + string.punctuation.replace('"', "").replace("\\", ""),
    ),
)
def test_strings_random(source: str) -> None:
    assert parse_program(repr(source)).pythonic() == (source,)
