from dataclasses import dataclass
from lox.Token import Token


@dataclass
class LoxRuntimeError(RuntimeError):
    token: Token
    message: str

class ParseError(RuntimeError):
    pass

@dataclass
class RaisedReturn(RuntimeError):
    """function returns are handled as raised errors as it's the easiest way to unwind"""
    value: object
