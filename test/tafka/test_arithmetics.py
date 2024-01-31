from test.tafka.emit import tafka_emit, tafka_text

from sleepy.tafka.representation import (
    Block,
    Const,
    Div,
    Int,
    Label,
    Load,
    Rem,
    Return,
    Set,
    Statement,
    Sum,
    Var,
)


def test_simple() -> None:
    source = "(sum (div 5 2) (rem (sum 2 2) 2))"
    tafka = tafka_emit(source)

    actual = tafka.main

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
        Return(),
    ]
    expected = Block(Label("main"), statements)

    assert actual == expected
    assert tafka_text(expected) == (
        "label(main):\n"
        "var(0): int = load(const(5): int): int\n"
        "var(1): int = load(const(2): int): int\n"
        "var(2): int = div(var(0): int, var(1): int): int\n"
        "var(3): int = load(const(2): int): int\n"
        "var(4): int = load(const(2): int): int\n"
        "var(5): int = sum(var(3): int, var(4): int): int\n"
        "var(6): int = load(const(2): int): int\n"
        "var(7): int = rem(var(5): int, var(6): int): int\n"
        "var(8): int = sum(var(2): int, var(7): int): int\n"
        "return\n"
    )
