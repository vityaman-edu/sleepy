from typing import cast, override

from sleepy.program import (
    Application,
    Bindings,
    Closure,
    Conditional,
    Definition,
    Expression,
    Integer,
    Kind,
    Namespace,
    Parameter,
    Program,
    ProgramNode,
    Symbol,
)
from sleepy.program.builtin import BuiltinLayer
from sleepy.program.unit import ProgramUnit

from .tree import Application as ApplicationAST
from .tree import IfExpression as IfExpressionAST
from .tree import Kind as KindAST
from .tree import Lambda as LambdaAST
from .tree import Program as ProgramAST
from .tree import Symbol as SymbolAST
from .tree import VariableDefinition as VariableDefinitionAST
from .tree import _Expression as ExpressionAST
from .tree import _Integer as IntegerAST
from .visitor import Visitor


class Syntax2Program(Visitor[ProgramNode]):
    def __init__(
        self,
        namespace: Namespace,
        bindings: Bindings,
    ) -> None:
        self.namespace = namespace
        self.bindings = bindings

    @override
    def visit_program(self, tree: ProgramAST) -> Program:
        return Program(
            statements=[
                self.visit_expression(expression)
                for expression in tree.expressions
            ],
        )

    @override
    def visit_conditional(self, tree: IfExpressionAST) -> Conditional:
        return Conditional(
            self.visit_expression(tree.condition.expression),
            self.visit_expression(tree.then_branch.expression),
            self.visit_expression(tree.else_branch.expression),
        )

    @override
    def visit_application(self, tree: ApplicationAST) -> ProgramNode:
        return Application(
            invokable=self.visit_expression(
                tree.invokable.expression,
            ),
            args=[self.visit_expression(arg) for arg in tree.args.expressions],
        )

    @override
    def visit_lambda(self, tree: LambdaAST) -> Closure:
        parent_namespace = self.namespace
        self.namespace = self.namespace.fork()

        for param in tree.parameters.parameters:
            self.namespace.define(Symbol(param.symbol.name))

        parameters = [
            Parameter(
                self.visit_symbol(parameter.symbol),
                self.visit_kind(parameter.kind),
            )
            for parameter in tree.parameters.parameters
        ]

        for parameter in parameters:
            self.bindings.bind(parameter.name, parameter)

        closure = Closure(parameters, statements=[])
        self.bindings.bind(
            self.namespace.define(Symbol("self")),
            closure,
        )

        closure.statements = [
            self.visit_expression(expression)
            for expression in tree.body.expressions
        ]

        self.namespace = parent_namespace
        return closure

    @override
    def visit_symbol(self, tree: SymbolAST) -> Symbol:
        return self.namespace.resolved(tree.name)

    @override
    def visit_kind(self, tree: KindAST) -> Kind:
        match tree.name.name:
            case "int":
                return Kind("int")
        raise NotImplementedError

    @override
    def visit_integer(self, tree: IntegerAST) -> Integer:
        return Integer(tree.value)

    @override
    def visit_definition(
        self,
        tree: VariableDefinitionAST,
    ) -> Definition:
        expression = self.visit_expression(tree.expression)
        symbol = self.namespace.define(Symbol(tree.symbol.name))
        self.bindings.bind(symbol, expression)
        return Definition(symbol, expression)

    @override
    def visit_expression(
        self,
        expression: ExpressionAST,
    ) -> Expression:
        return cast(Expression, super().visit_expression(expression))

    @classmethod
    def converted(cls, tree: ProgramAST) -> ProgramUnit:
        builtin = BuiltinLayer()
        s2p = Syntax2Program(builtin.namespace, builtin.bindings)
        program = s2p.visit_program(tree)
        return ProgramUnit(
            program=program,
            bindings=s2p.bindings,
            root=builtin.namespace,
        )
