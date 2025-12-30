
import unittest

from src.models import Case
from src.features.schema_validators import OverviewValidator, \
                                           EligibilityValidator, \
                                           DatesValidator, \
                                           LocationsValidator, \
                                           CostsValidator, \
                                           ContactValidator, \
                                           SchemaValidationEngine

class TestSchemaValidators(unittest.TestCase):
    def test_overview_validator(self):
        cases = [
            Case(call=OverviewValidator({"overview": {"title": "not provided"}}).validate_dict, outp=["overview"]),
            Case(call=OverviewValidator({"overview": {"title": "provided"}}).validate_dict, outp=[])
        ]

        for case in cases:
            self.assertTrue(case.test())

    def test_eligibility_validator(self):
        cases = [
            
        ]

unittest.main()