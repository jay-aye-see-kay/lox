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
        parser = Parser(tokens)
        expression = parser.parse()

        if self.had_error or expression == None:
            return

        Interpreter(self).interpret(expression)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def runtime_error(self, error: LoxRuntimeError):
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True
