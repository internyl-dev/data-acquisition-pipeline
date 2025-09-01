
from abc import ABC, abstractmethod

class SchemaCleaner(ABC):
    @abstractmethod
    def clean(self, schema:dict):
        "Standardizes the data in a schema"