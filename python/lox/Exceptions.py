from dataclasses import dataclass
from lox.Token import Token


@dataclass
class LoxRuntimeError(RuntimeError):
    token: Token
    message: str
