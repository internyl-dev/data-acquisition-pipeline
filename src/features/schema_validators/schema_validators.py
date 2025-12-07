
from .base_schema_validator import SchemaValidatorStrat
from src.models import Fields, BaseSchemaSection, RootSchema

from src.models import Fields, RootSchema
from src.models.schema_models import Overview, \
                                     Eligibility, \
                                     Dates, \
                                     Locations, \
                                     Costs, \
                                     Contact

class OverviewValidator(SchemaValidatorStrat):
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        if schema.overview.title == "not provided":
            target_info.append("overview" if return_str else Fields.OVERVIEW)
        return target_info
    
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        overview = schema["overview"]
        if overview["title"] == "not provided":
            target_info.append("overview" if return_str else Fields.OVERVIEW)
        return target_info


class EligibilityValidator(SchemaValidatorStrat):
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        eligibility: Eligibility = schema.eligibility
        eligibility_missing: bool = (
            "not provided" in eligibility.eligibility.grades
            and eligibility.eligibility.age.minimum == eligibility.eligibility.age.maximum
            and eligibility.eligibility.age.minimum == "not provided"
        )
        if eligibility_missing:
            target_info.append("eligibility" if return_str else Fields.ELIGIBILITY)
        return target_info
    
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        eligibility = schema["eligibility"]
        eligibility_missing: bool = (
            "not provided" in eligibility["eligibility"]["grades"]
            and list(eligibility["eligibility"]["age"].values()) == ["not provided", "not provided"]
        )
        if eligibility_missing:
            target_info.append("eligibility" if return_str else Fields.ELIGIBILITY)
        return target_info


class DatesValidator(SchemaValidatorStrat):
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        dates: Dates = schema.dates
        any_dates_missing: bool = any(
            deadline.date == "not provided" and deadline.rolling_basis != True 
            for deadline in dates.deadlines
        )
        application_deadline_missing: bool = not any(
            deadline.priority == "high" 
            for deadline in dates.deadlines
        )
        if any_dates_missing or application_deadline_missing:
            target_info.append("dates" if return_str else Fields.DATES)
        return target_info
    
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        dates = schema["dates"]
        any_dates_missing: bool = any(
            deadline["date"] == "not provided" and deadline["rolling_basis"] != True 
            for deadline in dates["deadlines"]
        )
        application_deadline_missing = not any(
            deadline["priority"] == "high" 
            for deadline in dates["deadlines"]
        )
        if any_dates_missing or application_deadline_missing:
            target_info.append("dates" if return_str else Fields.DATES)
        return target_info


class LocationsValidator(SchemaValidatorStrat):
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        locations: Locations = schema.locations
        any_virtual_unknown: bool = any(
            site.virtual == "not provided" 
            for site in locations.locations
        )
        if any_virtual_unknown:
            target_info.append("locations" if return_str else Fields.LOCATIONS)
        return target_info
    
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        locations = schema["locations"]
        any_virtual_unknown: bool = any(
            site["virtual"] == "not provided" 
            for site in locations["locations"]
        )
        if any_virtual_unknown:
            target_info.append("locations" if return_str else Fields.LOCATIONS)
        return target_info


class CostsValidator(SchemaValidatorStrat):
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        costs: Costs = schema.costs
        any_free_unknown: bool = any(
            plan.free == "not provided" 
            for plan in costs.costs
        )
        if any_free_unknown:
            target_info.append("costs" if return_str else Fields.COSTS)
        return target_info
    
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        costs = schema["costs"]
        any_free_unknown: bool = any(
            plan["free"] == "not provided" 
            for plan in costs["costs"]
        )
        if any_free_unknown:
            target_info.append("costs" if return_str else Fields.COSTS)
        return target_info


class ContactValidator(SchemaValidatorStrat):
    def validate(self, schema: RootSchema, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        contact: Contact = schema.contact
        contact_unknown: bool = [contact.contact.email, contact.contact.phone] == [
            "not provided", 
            "not provided"
        ]
        if contact_unknown:
            target_info.append("contact" if return_str else Fields.CONTACT)
        return target_info
    
    def validate_dict(self, schema: dict, return_str: bool = False) -> list[Fields] | list[str]:
        target_info = []
        contact = schema["contact"]
        contact_unknown: bool = list(contact["contact"].values()) == [
            "not provided", 
            "not provided"
        ]
        if contact_unknown:
            target_info.append("contact" if return_str else Fields.CONTACT)
        return target_info


class SchemaValidationEngine:
    def __init__(self) -> None:
        self.validators = [
            OverviewValidator,
            EligibilityValidator,
            DatesValidator,
            LocationsValidator,
            CostsValidator,
            ContactValidator,
        ]
    
    def validate(
        self, strat: type[SchemaValidatorStrat], schema: dict | BaseSchemaSection, return_str: bool = False) -> list[str] | list[Fields]:
        """Returns the field as an enum or string in a list if the field is missing needed information"""
        validator: SchemaValidatorStrat = strat()
        
        if isinstance(schema, RootSchema):
            return validator.validate(schema, return_str=return_str)
        else:
            assert isinstance(schema, dict)
            return validator.validate_dict(schema, return_str=return_str)
    
    def validate_all(self, schema: dict | BaseSchemaSection, return_str: bool = False) -> list[Fields] | list[str]:
        """Returns a list of all the enums/strings of all the fields that have missing needed information"""
        target_info = []
        
        for validator_class in self.validators:
            validator = validator_class()
            
            if isinstance(schema, BaseSchemaSection):
                info = validator.validate(schema, return_str=return_str)
            else:
                info = validator.validate_dict(schema, return_str=return_str)
            
            target_info.extend(info)
        
        return target_info
    
if __name__ == "__main__":
    from src.models import RootSchema

    root = RootSchema()
    validator = SchemaValidationEngine()
    print(validator.validate_all(root))
    
    str_validator = SchemaValidationEngine()
    print(str_validator.validate_all(root))