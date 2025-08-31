
from src.models import SchemaValidator

class OverviewValidator(SchemaValidator):
    def validate(self):
        required_info = []

        overview = self.schema['overview']
        if overview['title'] == 'not provided':
            required_info.append('overview')
        
        return required_info

class EligibilityValidator(SchemaValidator):
    def validate(self):
        required_info = []

        eligibility = self.schema['eligibility']
        if 'not provided' in eligibility['eligibility']['grades'] and list(eligibility['eligibility']['age'].values()) == ['not provided', 'not provided']:
            required_info.append('eligibility')
        
        return required_info

class DatesValidator(SchemaValidator):
    def validate(self):
        required_info = []

        dates = self.schema['dates']
        if (
            any([deadline['date'] == 'not provided' and deadline['rolling_basis'] != True for deadline in dates['deadlines']]) or
            not any([deadline['priority'] == 'high' for deadline in dates['deadlines']])
            ):
            required_info.append('dates')

        return required_info

class LocationsValidator(SchemaValidator):
    def validate(self):
        required_info = []

        locations = self.schema['locations']
        if any([site['virtual'] == 'not provided' for site in locations['locations']]):
            required_info.append('locations')

        return required_info

class CostsValidator(SchemaValidator):
    def validate(self):
        required_info = []

        costs = self.schema['costs']
        if any([plan['free'] == 'not provided' for plan in costs['costs']]):
            required_info.append('costs')

        return required_info

class ContactValidator(SchemaValidator):
    def validate(self):
        required_info = []

        contact = self.schema['contact']
        if list(contact['contact'].values()) == ['not provided', 'not provided']:
            required_info.append('contact')

        return required_info

class SchemaValidationEngine:
    def __init__(self, schema):
        self.validators = [OverviewValidator(schema),
                           EligibilityValidator(schema),
                           DatesValidator(schema),
                           LocationsValidator(schema),
                           CostsValidator(schema),
                           ContactValidator(schema)]


    def validate(self, strat:SchemaValidator, schema):
        return strat.validate(schema)
    
    def validate_all(self):
        required_info = []
        for validator in self.validators:
            required_info.extend(validator.validate())
        
        return required_info