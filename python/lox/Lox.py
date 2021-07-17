from lox.AstPrinter import AstPrinter
from lox.Parser import Parser
from lox.Scanner import Scanner


class Lox:
    hadError = False

    def runFile(self, filename: str):
        """Run one file as lox code"""
        source = open(filename).read()
        self.run(source)
        if self.hadError:
            exit(65)

    def runPrompt(self):
        """Run lox code as a repl"""
        while True:
            print("> ", end="")
            line = input()
            if not line:
                break
            self.run(line)
            self.hadError = False

    def run(self, source: str):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        expression = parser.parse()

        if self.hadError or expression == None:
            return

        print(AstPrinter().print(expression))

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.hadError = True
