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
        ("(def a 7) a", "7"),
        ("(def a 70) (def b 8) (sum a b)", "78"),
        (
            (
                "(def a 1) "
                "(def b a) "
                "(def a (sum 1 a)) "
                "(if (and (eq a 2) (eq b 1)) 1 0)"
            ),
            "1",
        ),
        ("(if (eq 1 0) (if (eq 1 1) 0 0) (if (eq 1 0) 0 1))", "1"),
    ],
)
def test_evaluate(src: str, res: str) -> None:
    assert evaluate(src) == res
