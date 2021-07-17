from __future__ import annotations
from typing import TYPE_CHECKING

from lox.TokenType import TokenType
from lox.Token import Token

if TYPE_CHECKING:
    from lox.Lox import Lox

tt = TokenType

keywords = {
    "and": tt.AND,
    "class": tt.CLASS,
    "else": tt.ELSE,
    "false": tt.FALSE,
    "for": tt.FOR,
    "fun": tt.FUN,
    "if": tt.IF,
    "nil": tt.NIL,
    "or": tt.OR,
    "print": tt.PRINT,
    "return": tt.RETURN,
    "super": tt.SUPER,
    "this": tt.THIS,
    "true": tt.TRUE,
    "var": tt.VAR,
    "while": tt.WHILE,
}


class Scanner:
    source: str
    tokens: list[Token]
    start = 0
    current = 0
    line = 0

    def __init__(self, source: str, lox: Lox):
        self.source = source
        self.lox = lox
        self.tokens = []

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(tt.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        char = self.advance()
        if char == "(":
            self.add_token(tt.LEFT_PAREN)
        elif char == ")":
            self.add_token(tt.RIGHT_PAREN)
        elif char == "{":
            self.add_token(tt.LEFT_BRACE)
        elif char == "}":
            self.add_token(tt.RIGHT_BRACE)
        elif char == ",":
            self.add_token(tt.COMMA)
        elif char == ".":
            self.add_token(tt.DOT)
        elif char == "-":
            self.add_token(tt.MINUS)
        elif char == "+":
            self.add_token(tt.PLUS)
        elif char == ";":
            self.add_token(tt.SEMICOLON)
        elif char == "*":
            self.add_token(tt.STAR)
        elif char == "!":
            self.add_token(tt.BANG_EQUAL if self.match("=") else tt.BANG)
        elif char == "=":
            self.add_token(tt.EQUAL_EQUAL if self.match("=") else tt.EQUAL)
        elif char == "<":
            self.add_token(tt.LESS_EQUAL if self.match("=") else tt.LESS)
        elif char == ">":
            self.add_token(tt.GREATER_EQUAL if self.match("=") else tt.GREATER)
        elif char == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(tt.SLASH)
        elif char == " " or char == "\r" or char == "\t":
            pass
        elif char == "\n":
            self.line += 1
        elif char == '"':
            self.string()
        else:
            if self.is_digit(char):
                self.number()
            elif self.is_alpha(char):
                self.identifier()
            else:
                self.lox.error(self.line, "Unexpected character.")

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        text = self.source[self.start : self.current]
        type = keywords.get(text, tt.IDENTIFIER)
        self.add_token(type)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        # look for a fractional part
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(tt.NUMBER, float(self.source[self.start : self.current]))

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.lox.error(self.line, "Unterminated string.")
            return
        # the closing "
        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(tt.STRING, value)

    def match(self, expected: str):
        """Like a conditional advance, only consumes the current character if it’s what we’re looking for"""
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        """Sort of like advance(), but doesn’t consume the character"""
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def is_alpha(self, char: str):
        return (
            (char >= "a" and char <= "z")
            or (char >= "A" and char <= "Z")
            or char == "_"
        )

    def is_alphanumeric(self, char: str):
        return self.is_alpha(char) or self.is_digit(char)

    def is_digit(self, char: str):
        return char >= "0" and char <= "9"

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        """Consumes the next character in the source file and returns it"""
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type: TokenType, literal: object = None):
        """Grabs the text of the current lexeme and creates a new token for it"""
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))
