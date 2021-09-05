from lox.Exceptions import RaisedReturn
from lox.Environment import Environment
from typing import TYPE_CHECKING, List
from lox.Stmt import Function
from lox.LoxCallable import LoxCallable

if TYPE_CHECKING:
    from lox.Interpreter import Interpreter

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment):
        self.closure = closure
        self.declaration = declaration

    def call(self, interpreter: "Interpreter", arguments: List[object]):
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except RaisedReturn as return_value:
            return return_value.value

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
