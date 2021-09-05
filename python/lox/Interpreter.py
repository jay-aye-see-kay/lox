from __future__ import annotations
from lox.LoxFunction import LoxFunction
from lox.LoxCallable import LoxCallable
from lox.Environment import Environment
from typing import List, TYPE_CHECKING, cast

from lox.Stmt import Block, Expression, Function, If, Return, Stmt, StmtVisitor, Var, While
from lox.Exceptions import LoxRuntimeError, RaisedReturn
from lox.Expr import Assign, Binary, Call, Expr, Grouping, Literal, Logical, Unary, ExprVisitor, Variable
from lox.Token import Token
from lox.TokenType import TokenType
from datetime import datetime

if TYPE_CHECKING:
    from lox.Lox import Lox

tt = TokenType


class ClockBuiltin(LoxCallable):
    def arity(self):
        return 0
    def call(self, interpreter: "Interpreter", arguments: List[object]):
        return datetime.now().timestamp()
    def __str__(self):
        return "<native fn>"


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, lox: Lox):
        super(Interpreter, self).__init__()
        self.lox = lox
        # always refers to outer env
        self.globals = Environment()
        # starts referring to outer env, but changes with scope
        self.environment = self.globals
        self.globals.define("clock", ClockBuiltin())

    def interpret(self, statements: List[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            self.lox.runtime_error(error)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def execute_block(self, statements: List[Stmt], new_environment: Environment):
        previous_environment = self.environment
        try:
            self.environment = new_environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous_environment

    def visit_block_stmt(self, stmt: Block):
        new_environment = Environment(self.environment)
        self.execute_block(stmt.statements, new_environment)

    def visit_expression_stmt(self, stmt: Expression):
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Function):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Expression):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt: Return):
        value = None
        if stmt.value != None:
            value = self.evaluate(stmt.value)
        raise RaisedReturn(value)

    def visit_var_stmt(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def is_truthy(self, obj: object):
        """like ruby; only False and None are falsy"""
        if obj is None:
            return False
        elif isinstance(obj, bool):
            return obj
        else:
            return True

    def stringify(self, obj: object):
        if obj is None:
            return "nil"
        elif isinstance(obj, float):
            text = str(obj)
            if text[-2:] == ".0":
                text = text[:-2]
            return text
        return str(obj)

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        left = cast(str, left)
        right = cast(str, right)

        if expr.operator.type == tt.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == tt.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == tt.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == tt.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)

        elif expr.operator.type == tt.BANG_EQUAL:
            return left != right
        elif expr.operator.type == tt.EQUAL_EQUAL:
            return left == right

        elif expr.operator.type == tt.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == tt.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            raise LoxRuntimeError(expr.operator, "operands must be numbers or strings")

        elif expr.operator.type == tt.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == tt.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        raise Exception("unreachable")

    def visit_call_expr(self, expr: Call):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        function = cast(LoxCallable, callee)
        if len(arguments) != function.arity():
            raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
        return function.call(self, arguments)

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_logical_expr(self, expr: Logical):
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left;
        else:
            if not self.is_truthy(left):
                return left;
        return self.evaluate(expr.right)


    def visit_unary_expr(self, expr: Unary):
        right = self.evaluate(expr.right)
        right = cast(str, right)

        if expr.operator.type == tt.MINUS:
            self.check_number_operands(expr.operator, right)
            return -float(right)
        elif expr.operator.type == tt.BANG:
            return not self.is_truthy(right)

        raise Exception("unreachable")

    def visit_variable_expr(self, expr: Variable):
        return self.environment.get(expr.name)

    def check_number_operands(self, operator: Token, *exprs: object):
        for expr in exprs:
            if not isinstance(expr, float):
                raise LoxRuntimeError(operator, "operands must be numbers")
