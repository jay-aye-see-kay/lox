from lox.Exceptions import LoxRuntimeError
from lox.Token import Token
from typing import Dict, Union


class Environment():
    def __init__(self, environment: Union["Environment", None] = None):
        self.enclosing = environment
        self.values: Dict[str, object] = {}

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: Token):
        value = self.values.get(name.lexeme)
        if value is not None:
            return value
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
