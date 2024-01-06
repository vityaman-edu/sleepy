from typing import cast

import pytest

from sleepy.program import (
    Application,
    Closure,
    Definition,
    Expression,
    Integer,
    ProgramUnit,
    Symbol,
)
from sleepy.program.builtin import intrinsics
from sleepy.program.namespace import NameNotFoundError

from .parse import parse


def binding(unit: ProgramUnit, name: str) -> Expression:
    return unit.bindings.resolve(unit.root.resolved(name))


def test_instrinsics() -> None:
    unit = parse("1")
    for intrinsic in intrinsics:
        assert intrinsic == binding(unit, intrinsic.name.name)


def test_root_definition() -> None:
    unit = parse(
        """
(def a 1)
(def b (sum 3 5))
(def c b)
""",
    )
    assert binding(unit, "a") == Integer(1)
    assert binding(unit, "b") == Application(
        Symbol("sum"),
        [Integer(3), Integer(5)],
    )
    assert binding(unit, "c") == Symbol("b")


def test_shadowing() -> None:
    unit = parse(
        """
(def a 1)
(def b (lambda () (def a 2)))
""",
    )
    assert binding(unit, "a") == Integer(1)

    assert unit.bindings.resolve(
        cast(
            Definition,
            cast(Closure, binding(unit, "b")).statements[0],
        ).symbol,
    ) == Integer(2)


def test_namepsace_fork() -> None:
    unit = parse(
        """
(def b (lambda () (def a 2)))
""",
    )

    with pytest.raises(NameNotFoundError):
        binding(unit, "a")


def test_redifinition() -> None:
    unit = parse(
        """
(def a 1)
(def a 2)
(def a a)
""",
    )

    assert unit.bindings.resolve(
        cast(Definition, unit.program.statements[0]).symbol,
    ) == Integer(1)

    assert unit.bindings.resolve(
        cast(Definition, unit.program.statements[1]).symbol,
    ) == Integer(2)

    assert unit.bindings.resolve(
        cast(Definition, unit.program.statements[2]).symbol,
    ) == Symbol("a")
