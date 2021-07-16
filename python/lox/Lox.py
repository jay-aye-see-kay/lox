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
        scanner = Scanner(source) # TODO Scanner can't use Lox.error()
        tokens = scanner.scan_tokens()
        for token in tokens:
            print(token)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.hadError = True
