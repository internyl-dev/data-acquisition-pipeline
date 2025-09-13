
import unittest

from features.ai_processors.prompt_constructors.instructions import INSTRUCTIONS
from src.features.ai_processors import create_chat_prompt_template, QueryBuilder
from src.models import ResponseModelFactory, Case

class TestAIProcessors(unittest.TestCase):
    def test_response_model_factory(self):
        cases = [
            Case(
                call=ResponseModelFactory().make_overview().model_fields.keys,
                outp={'title':"", 'provider':"", 'description':"", 'link':"", 'subject':"", 'tags':""}.keys()
                ),
            Case(
                call=ResponseModelFactory().make_eligibility().model_fields.keys,
                outp={"requirements": "", "eligibility": ""}.keys()
            ),
            Case(
                call=ResponseModelFactory().make_dates().model_fields.keys,
                outp={"deadlines": "", "dates": "", "duration_weeks": ""}.keys()
            ),
            Case(
                call=ResponseModelFactory().make_locations().model_fields.keys,
                outp={"locations": ""}.keys()
            ),
            Case(
                call=ResponseModelFactory().make_costs().model_fields.keys,
                outp={"costs": "", "stipend": ""}.keys()
            ),
            Case(
                call=ResponseModelFactory().make_contact().model_fields.keys,
                outp={"contact": ""}.keys()
            )
        ]

        for case in cases:
            self.assertTrue(
                case.test(),
                msg=f"{case.call} outputted {case.call()} which doesn't equal the expected output: {case.outp}"
            )
    
    def test_prompt_builder(self):
        cases = [
            Case(
                call=QueryBuilder().add_schema_context({"schema": "test"}).get_prompt_obj().get_prompt,
                outp='ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA:\n{"schema": "test"}'
            ),
            Case(
                call=QueryBuilder().add_title("title").get_prompt_obj().get_prompt,
                outp='TARGET PROGRAM INFORMATION:\nTitle: title'
            )
        ]

        for case in cases:
            self.assertTrue(
                case.test(),
                msg=f"{case.call} outputted {case.call()} which doesn't equal the expected output: {case.outp}"
            )
            
unittest.main()