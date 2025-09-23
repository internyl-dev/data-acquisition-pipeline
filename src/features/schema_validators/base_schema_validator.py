
from abc import ABC, abstractmethod
from typing import List

class SchemaValidatorStrat(ABC):
    "A strategy to determine which information to check is populated with necessary info"
    @abstractmethod
    def validate_dict(self, schema) -> List[str]:
        "Checks a portion of the dictionary schema to see if it is fully populated"

    @abstractmethod
    def validate(self, schema) -> List[str]:
        "Checks a portion of the BaseModel schema to see if it is fully populated"