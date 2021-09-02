from __future__ import annotations
from lox.Environment import Environment
from typing import List, TYPE_CHECKING, cast

from lox.Stmt import Expression, Stmt, StmtVisitor, Var
from lox.Exceptions import LoxRuntimeError
from lox.Expr import Binary, Expr, Grouping, Literal, Unary, ExprVisitor, Variable
from lox.Token import Token
from lox.TokenType import TokenType

if TYPE_CHECKING:
    from lox.Lox import Lox

tt = TokenType


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self, lox: Lox):
        super(Interpreter, self).__init__()
        self.lox = lox
        self.environment = Environment()

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

    def visit_expression_stmt(self, stmt: Expression):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: Expression):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

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

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

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
