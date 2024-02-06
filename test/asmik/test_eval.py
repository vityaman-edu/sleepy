from test.asmik.evaluate import evaluate

import pytest


@pytest.mark.parametrize(
    ("src", "res"),
    [
        ("0", "0"),
        ("1", "1"),
        ("2131", "2131"),
        ("-382", "-382"),
        ("(sum 2 2)", "4"),
        ("(sum 2 -2)", "0"),
        ("(div 2 2)", "1"),
        ("(rem 2 2)", "0"),
        ("(mul 2 2)", "4"),
        ("(sum 1 (sum 1 (sum 1 1)))", "4"),
        ("(if (eq 1 1) 6 9)", "6"),
        ("(if (eq 1 2) 6 9)", "9"),
        ("(if (eq (rem 2 2) 0) 1 0)", "1"),
        ("(if (eq (div 2 2) 0) 1 0)", "0"),
    ],
)
def test_evaluate(src: str, res: str) -> None:
    assert evaluate(src) == res
