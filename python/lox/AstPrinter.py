from lox.Expr import Binary, Expr, Grouping, Literal, Unary, Visitor


class AstPrinter(Visitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: Expr):
        out_str = "(" + name
        for expr in exprs:
            out_str += " "
            out_str += expr.accept(self)
        out_str += ")"
        return out_str

    def visit_binary_expr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        if expr.value == None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)
