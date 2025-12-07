
from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class Case(ABC):
    call: Callable[..., Any]
    args: list=field(default_factory=list)
    kwargs: dict=field(default_factory=dict)
    outp: Any=None

    def __post_init__(self):
        if self.args and self.kwargs:
            raise ValueError("Cannot specify both args and kwargs")
    
    def test(self):
        if self.args:
            try:
                return self.call(*self.args) == self.outp
            except Exception as e:
                print(f"Tried calling {self.call} with {self.args}, failed. Moving on to kwargs.\n{e}")

        try:
            return self.call(**self.kwargs) == self.outp
        except ExceptionGroup as e:
            print(f"Tried calling {self.call} with {self.kwargs}, failed.\n{e}")
            return