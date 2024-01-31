from test.tafka.emit import tafka_emit, tafka_text


def test_simple() -> None:
    source = (
        "(sum "
        "  (if (eq (sum 2 3) 5) "
        "    1 "
        "    (rem 2 2)) "
        "  (if (lt 2 3) "
        "    (mul 1 1) "
        "    0))"
    )

    actual = tafka_text(tafka_emit(source).main)

    lines = [
        "label(main):",
        "var(0): int = load(const(2): int): int",
        "var(1): int = load(const(3): int): int",
        "var(2): int = sum(var(0): int, var(1): int): int",
        "var(3): int = load(const(5): int): int",
        "var(4): bool = eq(var(2): int, var(3): int): bool",
        "if var(4): bool then label(0) else label(1) end label(2)",
        "label(0):",
        "  var(5): int = load(const(1): int): int",
        "  goto label(2)",
        "label(1):",
        "  var(6): int = load(const(2): int): int",
        "  var(7): int = load(const(2): int): int",
        "  var(8): int = rem(var(6): int, var(7): int): int",
        "  var(5): int = copy(var(8): int): int",
        "label(2):",
        "var(9): int = load(const(2): int): int",
        "var(10): int = load(const(3): int): int",
        "var(11): bool = lt(var(9): int, var(10): int): bool",
        "if var(11): bool then label(3) else label(4) end label(5)",
        "label(3):",
        "  var(12): int = load(const(1): int): int",
        "  var(13): int = load(const(1): int): int",
        "  var(14): int = mul(var(12): int, var(13): int): int",
        "  goto label(5)",
        "label(4):",
        "  var(15): int = load(const(0): int): int",
        "  var(14): int = copy(var(15): int): int",
        "label(5):",
        "var(16): int = sum(var(5): int, var(14): int): int",
        "return",
    ]

    expected = "\n".join(line.lstrip() for line in lines)
    assert actual == f"{expected}\n"