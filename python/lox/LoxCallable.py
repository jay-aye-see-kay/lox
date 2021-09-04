from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from lox.Interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: List[object]) -> object:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass
