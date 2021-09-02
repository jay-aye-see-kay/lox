

from lox.Exceptions import LoxRuntimeError
from lox.Token import Token
from typing import Dict


class Environment():
    values: Dict[str, object] = {}

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: Token):
        value = self.values[name.lexeme]
        if value:
            return value
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
