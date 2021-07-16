from lox.Lox import Lox

import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: lox [script]")
        exit(64)
    elif len(args) == 1:
        Lox().runFile(args[0])
    else:
        Lox().runPrompt()
