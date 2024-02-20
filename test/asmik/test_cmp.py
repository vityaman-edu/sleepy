from test.asmik.evaluate import evaluate

from hypothesis import given, strategies


@given(strategies.integers(0, 10))
def test_fibb(number: int) -> None:
    sleepy = f"""
    (def fibb (lambda (n int)
        (if (or (eq n 0) (eq n 1))
            1
            (sum
                (self (sum n -1))
                (self (sum n -2))))))
    (fibb {number})
    """

    def fibb(number: int) -> int:
        if number in (0, 1):
            return 1
        return fibb(number - 1) + fibb(number - 2)

    assert str(fibb(number)) == evaluate(sleepy)


@given(strategies.integers(0, 2**64 - 1))
def test_identity(number: int) -> None:
    sleepy = f"""
    ((lambda (n int) n) {number})
    """

    def identity(number: int) -> int:
        return number

    assert str(identity(number)) == evaluate(sleepy)


@given(strategies.integers(-(2**32), 2**32 - 1))
def test_sign(number: int) -> None:
    sleepy = f"""
    (
        (lambda (n int)
            (if (lt n 0) -1
            (if (lt 0 n)  1
                          0)))
        {number}
    )
    """

    def sign(number: int) -> int:
        if number < 0:
            return -1
        if number > 0:
            return 1
        return 0

    assert str(sign(number)) == evaluate(sleepy)


@given(strategies.integers(0, 40))
def test_sum(limit: int) -> None:
    sleepy = f"""
    (
        (lambda (n int) (if (eq n 0) 0 (sum n (self (sum n -1)))))
        {limit}
    )
    """

    assert str(sum(range(limit + 1))) == evaluate(sleepy)
