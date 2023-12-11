from sleepy.syntax import parse_program

source = """
(def result (
  (lambda (number int)
    (sum
      (if (eq (rem number 3))
        number
        (if (eq (rem number 5))
          number
          0)
      )
      (if (not (eq number 0))
        (self (sum number -1))
        0)))
  (sum 1000 -1)))
"""


def main() -> None:
    print(parse_program(source).pythonic())  # noqa: T201
