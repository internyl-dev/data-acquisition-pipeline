
import unittest

from src.features.ai_processors import create_chat_prompt_template, QueryBuilder
from src.models import Case

class TestPromptChain(unittest.TestCase):
    def test_query_builder(self):

        outputs = [
            'ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA:\n{"schema": "test"}', 
            'TARGET PROGRAM INFORMATION:\nTitle: title',
            'WEBPAGE CONTENTS START HERE:\nwebp contents'
        ]

        cases = [
            Case(
                call=QueryBuilder().add_schema_context({"schema": "test"}).get_prompt_obj().get_prompt,
                outp='\n'.join([outputs[0],'',''])
            ),
            Case(
                call=QueryBuilder().add_title("title").get_prompt_obj().get_prompt,
                outp='\n'.join(['',outputs[1],''])
            ),
            Case(
                call=QueryBuilder().add_schema_context({"schema": "test"}) \
                                   .add_title("title") \
                                   .get_prompt_obj().get_prompt,
                outp='\n'.join([outputs[0], outputs[1], ''])
            ),
            Case(
                call=QueryBuilder().add_title("title") \
                                   .add_schema_context({"schema": "test"}) \
                                   .get_prompt_obj().get_prompt,
                outp='\n'.join([outputs[0], outputs[1], ''])
            ),
            Case(
                call=QueryBuilder().add_title("title") \
                                   .add_schema_context({"schema": "test"}) \
                                   .add_webpage_contents("webp contents") \
                                   .get_prompt_obj().get_prompt,
                outp='\n'.join(outputs)
            )
        ]

        for case in cases:
            self.assertTrue(
                case.test(),
                msg=f"{case.call} outputted the following:\n{case.call()+"end"}\n which doesn't equal the expected output:\n{case.outp+"end"}"
            )

unittest.main()