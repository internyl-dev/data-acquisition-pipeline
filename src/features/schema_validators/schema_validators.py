
from .base_schema_validator import SchemaValidator
from src.models import Fields, BaseSchemaSection

class OverviewValidator(SchemaValidator):
    def validate_dict(self, schema:dict):
        target_info = []

        # Title missing
        overview = schema["overview"]
        if overview["title"] == "not provided":
            target_info.append("overview")
        
        return target_info
    
    def validate(self, schema):
        target_info = []
        
        # Title missing
        overview = schema.overview
        if overview.title == "not provided":
            target_info.append(Fields.OVERVIEW)

        return target_info

class EligibilityValidator(SchemaValidator):
    def validate_dict(self, schema:dict):
        target_info = []

        eligibility = schema["eligibility"]

        eligibility_missing = ("not provided" in eligibility["eligibility"]["grades"]) \
                               and (list(eligibility["eligibility"]["age"].values()) == ["not provided", "not provided"])

        if eligibility_missing:
            target_info.append("eligibility")
        
        return target_info
    
    def validate(self, schema):
        target_info = []
        
        eligibility = schema.eligibility

        eligibility_missing = ("not provided" in eligibility.grades) \
                              and (eligibility.age.minimum == eligibility.age.maximum) \
                              and (eligibility.age.minimum == "not provided")

        if eligibility_missing:
            target_info.append(Fields.ELIGIBILITY)

        return target_info

class DatesValidator(SchemaValidator):
    def validate_dict(self, schema:dict):
        target_info = []

        dates = schema["dates"]

        any_dates_missing = any([deadline["date"] == "not provided" and deadline["rolling_basis"] != True for deadline in dates["deadlines"]])
        applicaton_deadline_missing = not any([deadline["priority"] == "high" for deadline in dates["deadlines"]])

        if any_dates_missing or applicaton_deadline_missing:
            target_info.append("dates")

        return target_info
    
    def validate(self, schema):
        target_info = []

        dates = schema.dates

        any_dates_missing = any([deadline["date"] == "not provided" and deadline["rolling_basis"] != True for deadline in dates.deadlines])
        application_deadline_missing = not any([deadline["priority"] == "high" for deadline in dates.deadlines])

        if any_dates_missing or application_deadline_missing:
            target_info.append(Fields.DATES)

class LocationsValidator(SchemaValidator):
    def validate_dict(self, schema:dict):
        target_info = []

        locations = schema["locations"]
        
        any_virtual_unknown = any([site["virtual"] == "not provided" for site in locations["locations"]])

        if any_virtual_unknown:
            target_info.append("locations")

        return target_info
    
    def validate(self, schema):
        target_info = []

        locations = schema.locations

        any_virtual_unknown = any([site["virtual"] == "not provided" for site in locations.locations])

        if any_virtual_unknown:
            target_info.append(Fields.LOCATIONS)

        return target_info

class CostsValidator(SchemaValidator):
    def validate_dict(self, schema:dict):
        target_info = []

        costs = schema["costs"]
        
        any_free_unknown = any([plan["free"] == "not provided" for plan in costs["costs"]])
        
        if any_free_unknown:
            target_info.append("costs")

        return target_info
    
    def validate(self, schema):
        target_info = []

        costs = schema.costs

        any_free_unknown = any([plan["free"] == "not provided" for plan in costs["costs"]])

        if any_free_unknown:
            target_info.append(Fields.COSTS)

        return target_info

class ContactValidator(SchemaValidator):
    def validate_dict(self, schema:dict):
        target_info = []

        contact = schema["contact"]
        
        contact_unknown = list(contact["contact"].values()) == ["not provided", "not provided"]
        
        if contact_unknown:
            target_info.append("contact")

        return target_info
    
    def validate(self, schema):
        target_info = []

        contact = schema.contact

        contact_unknown = list(contact["contact"].values()) == ["not provided", "not provided"]

        if contact_unknown:
            target_info.append(Fields.CONTACT)

        return target_info

class SchemaValidationEngine:
    def __init__(self):
        self.validators = [
            OverviewValidator,
            EligibilityValidator,
            DatesValidator,
            LocationsValidator,
            CostsValidator,
            ContactValidator
        ]

    def validate(self, strat:SchemaValidator, schema) -> list[Fields]:
        "Returns the field as an enum in a list if the field is missing needed information"
        if isinstance(schema, BaseSchemaSection):
            return strat.validate(schema)
        elif isinstance(schema, dict):
            return strat.validate_dict(schema)
    
    def validate_all(self, schema) -> list[Fields]:
        "Returns a list of all the enums of all the fields that have missing needed information"
        target_info = []
        for validator in self.validators:
            if isinstance(schema, BaseSchemaSection):
                return target_info.extend(validator().validate(schema))
            elif isinstance(schema, dict):
                return target_info.extend(validator().validate_dict(schema))
        
        return target_info