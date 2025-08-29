
from abc import ABC, abstractmethod

class SchemaValidator(ABC):
    def __init__(self, schema):
        self.schema = schema

    @abstractmethod
    def validate(self):
        "Checks a portion of the schema to see if it is fully populated"