import pytest

from sleepy.syntax import Syntax2Program, parse_program
from sleepy.tool import formatted


def roundtrip(source: str) -> str:
    syntax_tree = parse_program(source)
    unit = Syntax2Program.converted(syntax_tree)
    return formatted(unit.program)


@pytest.mark.parametrize(
    ("source"),
    [
        "(def inc (lambda (x int) (sum x 1)))",
        "(eq 1 1)",
        """
(def fibb (lambda (n int)
  (if (or (eq n 0) (eq n 1))
    1
    (sum
      (self (sum n -1))
      (self (sum n -2))))))
""",
        # SPEC: problem 2
        """
(def fibb (lambda (n int)
  (if (or (eq n 0) (eq n 1))
    1
    (sum
      (self (sum n -1))
      (self (sum n -2))))))

(def iseven (lambda (x int)
  (eq (rem x 2) 0)))

(def sumfrom (lambda (n int)
  (def current
    (fibb n))
  (def addition
    (if (iseven current) current 0))
  (def hasnext
    (lt current 4000000000))
  (def next
    (if hasnext (self (sum n 1)) 0))
  (sum next addition)))

(def x 5)
(def r (sumfrom x))
""",
        # SPEC: problem 1
        """
(def result ((lambda (number int)
  (sum
    (if (eq (rem number 3))
      number
      (if (eq (rem number 5))
        number
        0)))
    (if (not (eq number 0))
      (self (sum number -1))
      0)) (sum 1000 -1)))
""",
    ],
)
def test_format_basic(source: str) -> None:
    assert roundtrip(source)[:-1] == " ".join(source.split())
