
from enum import Enum

class Fields(Enum):
    OVERVIEW = "overview"
    ELIGIBILITY = "eligibility"
    DATES = "dates"
    LOCATIONS = "locations"
    COSTS = "costs"
    CONTACT = "contact"
    METADATA = "metadata"
    ALL = "all"

if __name__ == "__main__":
    
    field = Fields.OVERVIEW

    print(field)

    print(isinstance(Fields.CONTACT, Fields))