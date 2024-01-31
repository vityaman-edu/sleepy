from sleepy.tafka.representation import (
    Block,
    Const,
    Copy,
    Div,
    Int,
    Load,
    Rem,
    Set,
    Statement,
    Sum,
    Var,
)


# (sum (div 5 2) (rem (sum 2 2) 2))
def test_example() -> None:
    statements: list[Statement] = [
        Set(Var("0", Int()), Load(Const("5", Int()))),
        Set(Var("1", Int()), Load(Const("2", Int()))),
        Set(Var("2", Int()), Div(Var("0", Int()), Var("1", Int()))),
        Set(Var("3", Int()), Load(Const("2", Int()))),
        Set(Var("4", Int()), Load(Const("2", Int()))),
        Set(Var("5", Int()), Sum(Var("3", Int()), Var("4", Int()))),
        Set(Var("6", Int()), Load(Const("2", Int()))),
        Set(Var("7", Int()), Rem(Var("5", Int()), Var("6", Int()))),
        Set(Var("8", Int()), Sum(Var("2", Int()), Var("7", Int()))),
        Set(Var("res", Int()), Copy(Var("8", Int()))),
    ]

    assert repr(Block(statements)) == (
        "var(0): int = load(const(5): int): int\n"
        "var(1): int = load(const(2): int): int\n"
        "var(2): int = div(var(0): int, var(1): int): int\n"
        "var(3): int = load(const(2): int): int\n"
        "var(4): int = load(const(2): int): int\n"
        "var(5): int = sum(var(3): int, var(4): int): int\n"
        "var(6): int = load(const(2): int): int\n"
        "var(7): int = rem(var(5): int, var(6): int): int\n"
        "var(8): int = sum(var(2): int, var(7): int): int\n"
        "var(res): int = copy(var(8): int): int"
    )
