
from abc import ABC, abstractmethod

class SchemaValidator(ABC):
    @abstractmethod
    def validate_dict(self, schema):
        "Checks a portion of the dictionary schema to see if it is fully populated"

    @abstractmethod
    def validate(self, schema):
        "Checks a portion of the BaseModel schema to see if it is fully populated"