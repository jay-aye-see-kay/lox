import sys

from lox.TokenType import TokenType
from lox.Token import Token
from lox.Expr import Binary, Literal, Grouping, Unary
from lox.AstPrinter import AstPrinter

from lox.Lox import Lox


if __name__ == "__main__":
    expr = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    print(AstPrinter().print(expr))
    # args = sys.argv[1:]
    # if len(args) > 1:
    #     print("Usage: lox [script]")
    #     exit(64)
    # elif len(args) == 1:
    #     Lox().runFile(args[0])
    # else:
    #     Lox().runPrompt()
