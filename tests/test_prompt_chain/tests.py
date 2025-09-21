
import unittest

from src.features.ai_processors import create_chat_prompt_template, QueryBuilder
from src.models import Case

class TestPromptChain(unittest.TestCase):
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