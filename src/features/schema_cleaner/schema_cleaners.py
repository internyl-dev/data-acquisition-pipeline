
from src.assets import STATE_ABBREVIATIONS
from .base_schema_cleaner import SchemaCleaner

class OverviewCleaner(SchemaCleaner):
    def __init__(self, schema:dict):
        self.overview = schema["overview"]

    def _fix_no_subjects(self):
        # If no subjects were found but for some reason
        # the model didn't include "Various"
        if not self.overview['subject']:
            self.overview['subject'] = ['Various']

    def clean(self):
        self._fix_no_subjects()



class EligibilityCleaner(SchemaCleaner):
    def __init__(self, schema:dict):
        self.eligibility = schema["eligibility"]

    def clean(self):
        pass



class DatesCleaner(SchemaCleaner):
    def __init__(self, schema:dict):
        self.dates = schema["dates"]

    def clean(self):
        pass



class LocationsCleaner(SchemaCleaner):
    def __init__(self, schema:dict):
        self.locations = schema["locations"]

    def _fix_state_abbrevs(self):
        for location in self.locations['locations']:

            for abbreviation in STATE_ABBREVIATIONS:
                location['state'] = location['state'].replace(abbreviation, STATE_ABBREVIATIONS[abbreviation])

    def clean(self):
        self._fix_state_abbrevs()



class CostsCleaner(SchemaCleaner):
    def __init__(self, schema:dict):
        self.costs = schema["costs"]

    def _fix_free(self):
        # If the highest and lowest cost 
        # were included as 0
        for cost in self.costs['costs']:

            # Exit to avoid error
            if not cost:
                break

            if cost['lowest'] == 0 and cost['highest'] == 0:
                cost['lowest'], cost['highest'] = (None, None)
                cost['free'] = True

    def _fix_not_free(self):
        # If costs were included but
        # they weren't marked as not free
        for cost in self.costs['costs']:

            if any((isinstance(x, float) or isinstance(x, int)) for x in (cost['lowest'], cost['highest'])):
                cost['free'] = False

    def _fix_null_stipend(self):
        # If stipend is available
        # and marked as null
        stipend = self.costs['stipend']
        if (stipend['available'] == True) and (stipend['amount'] == None):
            stipend['amount'] = "not provided"

    def clean(self):
        self._fix_free()
        self._fix_not_free()
        self._fix_null_stipend()



class ContactCleaner(SchemaCleaner):
    def __init__(self, schema:dict):
        self.contact = schema["contact"]

    def clean(self):
        pass
