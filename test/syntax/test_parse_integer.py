import pytest
from hypothesis import given
from hypothesis import strategies as st

from sleepy.syntax import SleepySyntaxError, parse_program


@pytest.mark.parametrize(
    ("source", "output"),
    [
        ("+0", 0),
        ("-0", 0),
        ("1", 1),
        ("-1", -1),
        ("46432343453", 46432343453),
        ("-32642642324", -32642642324),
    ],
)
def test_integer_positive(source: str, output: int) -> None:
    assert parse_program(source).pythonic() == (output,)


@pytest.mark.parametrize(
    ("source"),
    ["++0", "--0", "-", "+", "", "2121.0", "21321.5"],
)
def test_integer_failure(source: str) -> None:
    with pytest.raises(SleepySyntaxError):
        parse_program(source)


@given(st.integers())
def test_integer_random(integer: int) -> None:
    assert parse_program(str(integer)).pythonic() == (integer,)
