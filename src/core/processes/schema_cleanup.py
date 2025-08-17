
from ...assets import STATE_ABBREVIATIONS

class SchemaCleanup:

    def cleanup_overview(self):
        overview = self.response['overview']

        # If no subjects were found but for some reason
        # the model didn't include "Various"
        if not overview['subject']:
            overview['subject'] = ['Various']

    def cleanup_eligibility(self):
        eligibility = self.response['eligibility']

    def cleanup_dates(self):
        dates = self.response['dates']

    def cleanup_locations(self):
        locations = self.response['locations']

        for location in locations:

            for abbreviation in STATE_ABBREVIATIONS:
                location['state'] = location['state'].replace(abbreviation, STATE_ABBREVIATIONS[abbreviation])

    def cleanup_costs(self):
        costs = self.response['costs']

        # If the highest and lowest cost 
        # were included as 0
        for cost in costs['costs']:

            if cost['lowest'] == 0 and cost['highest'] == 0:
                cost['lowest'], cost['highest'] = (None, None)
                cost['free'] = True

        # If costs were included but
        # they weren't marked as not free
        for cost in costs['costs']:

            if any((isinstance(x, float) or isinstance(x, int)) for x in (cost['lowest'], cost['highest'])):
                cost['free'] = False
        
        if (cost['stipend']['available'] == True):
            cost['stipend']['amount'] = None
                
    def cleanup_contact(self):
        contact = self.response['contact']

    def cleanup_main(self):
        self.cleanup_overview()
        self.cleanup_eligibility()
        self.cleanup_dates()
        self.cleanup_locations()
        self.cleanup_costs()
        self.cleanup_contact()