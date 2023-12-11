from lark.tree import Meta

from . import (
    Application,
    Args,
    Body,
    Condition,
    ElseBranch,
    Expression,
    IfExpression,
    Integer,
    Invokable,
    Kind,
    Lambda,
    Parameter,
    Parameters,
    Program,
    Symbol,
    ThenBranch,
    VariableDefinition,
)


def program(*expr: Expression) -> Program:
    return Program(Meta(), expressions=[*expr])


def define(name: str, expr: Expression) -> VariableDefinition:
    return VariableDefinition(
        Meta(),
        symbol=Symbol(Meta(), name),
        expression=expr,
    )


def integer(value: int) -> Integer:
    return Integer(Meta(), value)


def symbol(value: str) -> Symbol:
    return Symbol(Meta(), value)


def kind(name: str) -> Kind:
    return Kind(Meta(), symbol(name))


def func(
    parameters: list[tuple[str, str]],
    body: list[Expression],
) -> Lambda:
    return Lambda(
        Meta(),
        Parameters(
            Meta(),
            [
                Parameter(Meta(), symbol(name), kind(typename))
                for (name, typename) in parameters
            ],
        ),
        Body(Meta(), body),
    )


def if_stmt(
    condition: Expression,
    then_branch: Expression,
    else_branch: Expression,
) -> IfExpression:
    return IfExpression(
        Meta(),
        Condition(Meta(), condition),
        ThenBranch(Meta(), then_branch),
        ElseBranch(Meta(), else_branch),
    )


def invoke(
    invokable: Expression,
    *args: Expression,
) -> Application:
    return Application(
        Meta(),
        Invokable(Meta(), invokable),
        Args(Meta(), [*args]),
    )
