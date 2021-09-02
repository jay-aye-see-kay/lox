from typing import Union
from lox.Token import Token
from lox.TokenType import TokenType
from lox.Exceptions import LoxRuntimeError
from lox.Interpreter import Interpreter
from lox.Parser import Parser
from lox.Scanner import Scanner


class Lox:
    had_error = False
    had_runtime_error = False

    def run_file(self, filename: str):
        """Run one file as lox code"""
        source = open(filename).read()
        self.run(source)
        if self.had_error:
            exit(65)
        if self.had_runtime_error:
            exit(70)

    def run_prompt(self):
        """Run lox code as a repl"""
        while True:
            print("> ", end="")
            line = input()
            if not line:
                break
            self.run(line)
            self.had_error = False

    def run(self, source: str):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self)
        statements = parser.parse()

        if self.had_error or len(statements) == 0:
            return

        Interpreter(self).interpret(statements)

    def error(self, token: Union[int, Token], message: str):
        if isinstance(token, int):
            # the book overloads this method to take a token or line_no
            line = token
            self.report(line, "", message)
        elif token.type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def runtime_error(self, error: LoxRuntimeError):
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True
