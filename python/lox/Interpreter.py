from typing import cast
from lox.Expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from lox.TokenType import TokenType

tt = TokenType


class Interpreter(Visitor):
    def interpret(self, expression):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except expression as error:
            print("error", error)  # TODO

    def evaluate(self, expr: Expr):
        return expr.accept(self)

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
            return float(left) > float(right)
        elif expr.operator.type == tt.GREATER_EQUAL:
            return float(left) >= float(right)
        elif expr.operator.type == tt.LESS:
            return float(left) < float(right)
        elif expr.operator.type == tt.LESS_EQUAL:
            return float(left) <= float(right)

        elif expr.operator.type == tt.BANG_EQUAL:
            return left != right
        elif expr.operator.type == tt.EQUAL_EQUAL:
            return left == right

        elif expr.operator.type == tt.MINUS:
            return float(left) - float(right)
        elif expr.operator.type == tt.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right

        elif expr.operator.type == tt.SLASH:
            return float(left) / float(right)
        elif expr.operator.type == tt.STAR:
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
            return -float(right)
        elif expr.operator.type == tt.BANG:
            return not self.is_truthy(right)

        raise Exception("unreachable")
