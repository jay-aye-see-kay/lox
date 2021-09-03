from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union

from lox.Expr import Expr
from lox.Token import Token


class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: "Block"):
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression"):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: "If"):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print"):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var"):
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        pass


@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block_stmt(self)


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Union[Stmt, None]

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)
