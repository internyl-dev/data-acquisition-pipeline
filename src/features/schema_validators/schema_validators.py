
from typing import List
from .base_schema_validator import SchemaValidatorStrat
from src.models import Fields, BaseSchemaSection

class OverviewValidator(SchemaValidatorStrat):
    def __init__(self, return_str:bool=False):
        if return_str:
            self.info = "overview"
        else:
            self.info = Fields.OVERVIEW
            
    def validate_dict(self, schema:dict):
        target_info = []

        # Title missing
        overview = schema["overview"]
        if overview["title"] == "not provided":
            target_info.append(self.info)
        
        return target_info
    
    def validate(self, schema):
        target_info = []
        
        # Title missing
        overview = schema.overview
        if overview.title == "not provided":
            target_info.append(self.info)

        return target_info

class EligibilityValidator(SchemaValidatorStrat):
    def __init__(self, return_str:bool=False):
        if return_str:
            self.info = "eligibility"
        else:
            self.info = Fields.ELIGIBILITY

    def validate_dict(self, schema:dict):
        target_info = []

        eligibility = schema["eligibility"]

        eligibility_missing = ("not provided" in eligibility["eligibility"]["grades"]) \
                               and (list(eligibility["eligibility"]["age"].values()) == ["not provided", "not provided"])

        if eligibility_missing:
            target_info.append(self.info)
        
        return target_info
    
    def validate(self, schema):
        target_info = []
        
        eligibility = schema.eligibility

        eligibility_missing = ("not provided" in eligibility.eligibility.grades) \
                              and (eligibility.eligibility.age.minimum == eligibility.eligibility.age.maximum) \
                              and (eligibility.eligibility.age.minimum == "not provided")

        if eligibility_missing:
            target_info.append(self.info)

        return target_info

class DatesValidator(SchemaValidatorStrat):
    def __init__(self, return_str:bool=False):
        if return_str:
            self.info = "dates"
        else:
            self.info = Fields.DATES

    def validate_dict(self, schema:dict):
        target_info = []

        dates = schema["dates"]

        any_dates_missing = any([deadline["date"] == "not provided" and deadline["rolling_basis"] != True for deadline in dates["deadlines"]])
        applicaton_deadline_missing = not any([deadline["priority"] == "high" for deadline in dates["deadlines"]])

        if any_dates_missing or applicaton_deadline_missing:
            target_info.append(self.info)

        return target_info
    
    def validate(self, schema):
        target_info = []

        dates = schema.dates

        any_dates_missing = any([deadline.date == "not provided" and deadline.rolling_basis != True for deadline in dates.deadlines])
        application_deadline_missing = not any([deadline.priority == "high" for deadline in dates.deadlines])

        if any_dates_missing or application_deadline_missing:
            target_info.append(self.info)

        return target_info

class LocationsValidator(SchemaValidatorStrat):
    def __init__(self, return_str:bool=False):
        if return_str:
            self.info = "locations"
        else:
            self.info = Fields.LOCATIONS

    def validate_dict(self, schema:dict):
        target_info = []

        locations = schema["locations"]
        
        any_virtual_unknown = any([site["virtual"] == "not provided" for site in locations["locations"]])

        if any_virtual_unknown:
            target_info.append(self.info)

        return target_info
    
    def validate(self, schema):
        target_info = []

        locations = schema.locations

        any_virtual_unknown = any([site.virtual == "not provided" for site in locations.locations])

        if any_virtual_unknown:
            target_info.append(self.info)

        return target_info

class CostsValidator(SchemaValidatorStrat):
    def __init__(self, return_str:bool=False):
        if return_str:
            self.info = "costs"
        else:
            self.info = Fields.COSTS

    def validate_dict(self, schema:dict):
        target_info = []

        costs = schema["costs"]
        
        any_free_unknown = any([plan["free"] == "not provided" for plan in costs["costs"]])
        
        if any_free_unknown:
            target_info.append(self.info)

        return target_info
    
    def validate(self, schema):
        target_info = []

        costs = schema.costs

        any_free_unknown = any([plan.free == "not provided" for plan in costs.costs])

        if any_free_unknown:
            target_info.append(self.info)

        return target_info

class ContactValidator(SchemaValidatorStrat):
    def __init__(self, return_str:bool=False):
        if return_str:
            self.info = "contact"
        else:
            self.info = Fields.CONTACT

    def validate_dict(self, schema:dict):
        target_info = []

        contact = schema["contact"]
        
        contact_unknown = list(contact["contact"].values()) == ["not provided", "not provided"]
        
        if contact_unknown:
            target_info.append(self.info)

        return target_info
    
    def validate(self, schema):
        target_info = []

        contact = schema.contact

        contact_unknown = [contact.contact.email, contact.contact.phone] == ["not provided", "not provided"]

        if contact_unknown:
            target_info.append(self.info)

        return target_info

class SchemaValidationEngine:
    def __init__(self, return_str:bool=False):
        self.return_str = return_str
        self.validators = [
            OverviewValidator,
            EligibilityValidator,
            DatesValidator,
            LocationsValidator,
            CostsValidator,
            ContactValidator
        ]

    def validate(self, strat:SchemaValidatorStrat, schema:dict|BaseSchemaSection) -> list[Fields]:
        "Returns the field as an enum in a list if the field is missing needed information"
        if isinstance(schema, BaseSchemaSection):
            return strat(self.return_str).validate(schema)
        elif isinstance(schema, dict):
            return strat(self.return_str).validate_dict(schema)
    
    def validate_all(self, schema:dict|BaseSchemaSection, return_str:bool=False) -> list[Fields]:
        "Returns a list of all the enums of all the fields that have missing needed information"
        target_info = []
        for validator in self.validators:
            if isinstance(schema, BaseSchemaSection):
                info = validator(self.return_str).validate(schema)
            elif isinstance(schema, dict):
                info = validator(self.return_str).validate_dict(schema)
            print(info)
            target_info.extend(info)
        
        return target_info
    
if __name__ == "__main__":
    from src.models import RootSchema

    root = RootSchema()
    validator = SchemaValidationEngine()
    print(validator.validate_all(root))
    
    str_validator = SchemaValidationEngine(return_str=True)
    print(str_validator.validate_all(root))