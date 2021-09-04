from lox.Environment import Environment
from typing import TYPE_CHECKING, List
from lox.Stmt import Function
from lox.LoxCallable import LoxCallable

if TYPE_CHECKING:
    from lox.Interpreter import Interpreter

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function):
        self.declaration = declaration

    def call(self, interpreter: "Interpreter", arguments: List[object]):
        environment = Environment(interpreter.globals)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        interpreter.execute_block(self.declaration.body, environment)

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
