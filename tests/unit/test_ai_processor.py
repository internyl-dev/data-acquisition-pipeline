
import unittest

from src.models import SchemaModelFactory, Case

class TestAIProcessors(unittest.TestCase):
    def test_response_model_factory(self):
        cases = [
            Case(
                call=SchemaModelFactory().make_overview().model_fields.keys,
                outp={'title':"", 'provider':"", 'description':"", 'link':"", 'subject':"", 'tags':""}.keys()
                ),
            Case(
                call=SchemaModelFactory().make_eligibility().model_fields.keys,
                outp={"requirements": "", "eligibility": ""}.keys()
            ),
            Case(
                call=SchemaModelFactory().make_dates().model_fields.keys,
                outp={"deadlines": "", "dates": "", "duration_weeks": ""}.keys()
            ),
            Case(
                call=SchemaModelFactory().make_locations().model_fields.keys,
                outp={"locations": ""}.keys()
            ),
            Case(
                call=SchemaModelFactory().make_costs().model_fields.keys,
                outp={"costs": "", "stipend": ""}.keys()
            ),
            Case(
                call=SchemaModelFactory().make_contact().model_fields.keys,
                outp={"contact": ""}.keys()
            )
        ]

        for case in cases:
            self.assertTrue(
                case.test(),
                msg=f"{case.call} outputted {case.call()} which doesn't equal the expected output: {case.outp}"
            )
            
unittest.main()