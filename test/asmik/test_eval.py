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
            """
            (def a 1)
            (def b a)
            (def a (sum 1 a))
            (if (and (eq a 2) (eq b 1)) 1 0)
            """,
            "1",
        ),
        ("(if (eq 1 0) (if (eq 1 1) 0 0) (if (eq 1 0) 0 1))", "1"),
        (
            """
            (def id (lambda (n int) n))
            (def a (id 1))
            (def b (id 11))
            (def c (id 111))
            (if (and (eq a 1)
                (and (eq b 11)
                     (eq c 111))) 1 0)
            """,
            "1",
        ),
        (
            """
            (def qsum (lambda (a int b int)
                (sum (mul a a) (mul b b))))
            (if (and (eq (qsum 1 2) 5)
                (and (eq (qsum 2 2) 8)
                     (eq (qsum 1 1) 2))) 1 0)
            """,
            "1",
        ),
        (
            """
            (def id (lambda (n int)
                (if (eq n 0) 0 (sum (self (sum n -1)) 1))))
            (if (and (eq (id 1) 1)
                (and (eq (id 2) 2)
                     (eq (id 3) 3))) 1 0)
            """,
            "1",
        ),
        (
            """
            (def fibb (lambda (n int)
                (if (or (eq n 0) (eq n 1))
                    1
                    (sum
                        (self (sum n -1))
                        (self (sum n -2))))))
            (if (and (eq (fibb 0) 1)
                (and (eq (fibb 1) 1)
                (and (eq (fibb 2) 2)
                (and (eq (fibb 3) 3)
                (and (eq (fibb 4) 5)
                     (eq (fibb 5) 8)))))) 1 0)
            """,
            "1",
        ),
    ],
)
def test_evaluate(src: str, res: str) -> None:
    assert evaluate(src) == res
