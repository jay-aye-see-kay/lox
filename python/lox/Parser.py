from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lox.Lox import Lox
from lox.Exceptions import ParseError
from typing import List
from lox.Stmt import Block, Expression, If, Print, Stmt, Var, While
from lox.Expr import Assign, Binary, Logical, Unary, Literal, Grouping, Variable
from lox.TokenType import TokenType
from lox.Token import Token


tt = TokenType


class Parser:
    current = 0

    def __init__(self, tokens: list[Token], lox: "Lox"):
        self.tokens = tokens
        self.lox = lox

    def parse(self):
        statements: List[Stmt] = []
        while not self.is_at_end():
            statement = self.declaration()
            if statement:
                statements.append(statement)
        return statements

    def expression(self):
        return self.assignment()

    def declaration(self):
        try:
            if self.match(tt.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError as _:
            self.synchronize()
            return None

    def statement(self) -> Stmt:
        if self.match(tt.FOR):
            return self.for_statement()
        if self.match(tt.IF):
            return self.if_statement()
        if self.match(tt.PRINT):
            return self.print_statement()
        if self.match(tt.WHILE):
            return self.while_statement()
        if self.match(tt.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self):
        self.consume(tt.LEFT_PAREN, "Expect '(' after 'for'.")
        # look for the initializer
        if self.match(tt.SEMICOLON):
            initializer = None
        elif self.match(tt.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        # look for the condition
        condition = None
        if not self.check(tt.SEMICOLON):
            condition = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after loop condition")
        # look for the increment
        increment = None
        if not self.check(tt.RIGHT_PAREN):
            increment = self.expression()
        self.consume(tt.RIGHT_PAREN, "Expect ')' after for clauses.")
        # the body
        body = self.statement()
        # desugaring: put the increment at the end of the body
        if increment is not None:
            body = Block([body, Expression(increment)])
        # desugaring: make a while loop, default condition true
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        # desugaring: add the initializer before the while loop
        if initializer is not None:
            body = Block([initializer, body])
        # done
        return body


    def if_statement(self) -> Stmt:
        self.consume(tt.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(tt.RIGHT_PAREN, "Expect ')' after condition.")
        then_branch = self.statement()
        else_branch = self.statement() if self.match(tt.ELSE) else None
        return If(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def var_declaration(self):
        name = self.consume(tt.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(tt.EQUAL):
            initializer = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after variable declaration.")
        if initializer is None:
            # HACK because python is non-nullable:
            # create a "fake token" of value None to store as variable value
            initializer = Literal(Token(tt.IDENTIFIER, "", None, name.line))
        return Var(name, initializer)

    def while_statement(self):
        self.consume(tt.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(tt.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def expression_statement(self):
        expr = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def block(self):
        statements: List[Stmt] = []
        while not self.check(tt.RIGHT_BRACE) and not self.is_at_end():
            statement = self.declaration()
            if statement:
                statements.append(statement)
        self.consume(tt.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self):
        expr = self.logical_or()
        if self.match(tt.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def logical_or(self):
        expr = self.logical_and()
        while self.match(tt.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        return expr

    def logical_and(self):
        expr = self.equality()
        while self.match(tt.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(tt.GREATER, tt.GREATER_EQUAL, tt.LESS, tt.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(tt.MINUS, tt.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(tt.SLASH, tt.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(tt.BANG, tt.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self):
        if self.match(tt.FALSE):
            return Literal(False)
        if self.match(tt.TRUE):
            return Literal(True)
        if self.match(tt.NIL):
            return Literal(None)
        if self.match(tt.NUMBER, tt.STRING):
            return Literal(self.previous().literal)
        if self.match(tt.IDENTIFIER):
            return Variable(self.previous())
        if self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        # TODO proper exception
        raise Exception(self.peek(), "Expect expression.")

    def match(self, *types: TokenType):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, type: TokenType):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == tt.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str) -> ParseError:
        self.lox.error(token, message)
        return ParseError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            # after a semicolon, we’re probably finished with a statement
            if self.previous().type == tt.SEMICOLON:
                return
            # Most statements start with a keyword—for, if, return, var, etc.
            # When the next token is any of those, we’re probably about to
            # start a statement.
            if self.peek().type in [tt.CLASS, tt.FUN, tt.VAR, tt.FOR, tt.IF, tt.WHILE, tt.PRINT, tt.RETURN]: 
                return
            self.advance()


