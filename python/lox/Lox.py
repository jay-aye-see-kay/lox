import sys


class Lox:
    hadError = False

    def main(self, args: list[str]):
        if len(args) > 1:
            print("Usage: lox [script]")
            exit(64)
        elif len(args) == 1:
            self.runFile(args[0])
        else:
            self.runPrompt()

    def runFile(self, filename: str):
        source = open(filename).read()
        self.run(source)
        if self.hadError:
            exit(65)

    def runPrompt(self):
        while True:
            print("> ", end="")
            line = input()
            if not line:
                break
            self.run(line)
            self.hadError = False

    def run(self, source: str):
        scanner = Scanner(source)
        tokens = scanner.scanTokens()
        for token in tokens:
            print(token)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.hadError = True


if __name__ == "__main__":
    Lox().main(sys.argv[1:])
