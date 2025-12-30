
import unittest
from src.models.schema_models import Overview, \
                                     Eligibility, \
                                     Dates, \
                                     Locations, \
                                     Costs, \
                                     Contact, \
                                     Metadata
                                     
class TestSchemaSections(unittest.TestCase):
    def test_overview(self):
        obj = Overview()
        model_dict =   {
            "title": "not provided",
            "provider": "not provided",
            "description": "not provided",

            "link": "not provided",
            "subject": ["not provided"],
            "tags": ["not provided"]
        }

        self.assertDictEqual(model_dict, obj.model_dump())

    def test_eligibility(self):
        obj = Eligibility()
        model_dict =   {
            "requirements": {
                "essay_required": "not provided",
                "recommendation_required": "not provided",
                "transcript_required": "not provided",
                "other": ["not provided"]
            },

            "eligibility": {
                "grades": ["not provided"],
                "age": {
                    "minimum": "not provided",
                    "maximum": "not provided"
                }
            }
        }

        self.assertDictEqual(model_dict, obj.model_dump())

    def test_dates(self):
        obj = Dates()
        model_dict =   {
            "deadlines": [
                {
                    "name": "not provided",
                    "priority": "not provided",
                    "term": "not provided",
                    "date": "not provided",
                    "rolling_basis": "not provided",
                    "time": "not provided"
                }
            ],

            "dates": [
                {
                    "term": "not provided",
                    "start": "not provided",
                    "end": "not provided"
                }
            ],

            "duration_weeks": "not provided"
        }

        self.assertDictEqual(model_dict, obj.model_dump())

    def test_locations(self):
        obj = Locations()
        model_dict =   {
            "locations": [
                {
                    "virtual": "not provided",
                    "state": "not provided",
                    "city": "not provided",
                    "address": "not provided" 
                }
            ]
        }

        self.assertDictEqual(model_dict, obj.model_dump())

    def test_costs(self):
        obj = Costs()
        model_dict =   {
            "costs": [
                {
                    "name": "not provided",
                    "free": "not provided",
                    "lowest": "not provided",
                    "highest": "not provided",
                    "financial_aid_available": "not provided"
                }
            ],

            "stipend": {
                "available": "not provided",
                "amount": "not provided"
            }
        }

        self.assertDictEqual(model_dict, obj.model_dump())

    def test_contact(self):
        obj = Contact()
        model_dict =   {
            "contact": {
                "email": "not provided",
                "phone": "not provided"
            }
        }

        self.assertDictEqual(model_dict, obj.model_dump())

    def test_metadata(self):
        obj = Metadata()
        model_dict =   {
            "date_added": "",
            "time_added": "",
            "favicon": "",
            "total_input_tokens": 0,
            "total_output_tokens": 0
        }

        self.assertDictEqual(model_dict, obj.model_dump())

unittest.main()