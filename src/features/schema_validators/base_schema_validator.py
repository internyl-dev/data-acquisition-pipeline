
from abc import ABC, abstractmethod

from src.models import Fields, RootSchema

class SchemaValidatorStrat(ABC):
    "A strategy to determine which information to check is populated with necessary info"
    @abstractmethod
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        "Checks a portion of the BaseModel schema to see if it is fully populated"

    @abstractmethod
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        "Checks a portion of the dictionary schema to see if it is fully populated"