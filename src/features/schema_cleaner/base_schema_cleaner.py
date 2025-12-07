
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from src.models import BaseSchemaSection

T = TypeVar("T", bound=BaseSchemaSection)

class SchemaCleaner(ABC, Generic[T]):
    @abstractmethod
    def clean(self, section: dict | T) -> None:
        "Standardizes the data in a schema"