from abc import ABC, abstractmethod
from dataclasses import dataclass

from lox.Expr import Expr


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, expr: "Expression"):
        pass

    @abstractmethod
    def visit_print_stmt(self, expr: "Print"):
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        pass


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)
