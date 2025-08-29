
from abc import ABC
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Case(ABC):
    call: Callable[..., Any]
    args: dict={}
    outp: any=None