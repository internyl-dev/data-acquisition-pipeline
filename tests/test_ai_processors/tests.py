
import unittest

#from src.features.ai_processors import create_chat_prompt_template
from src.models import ResponseModelFactory, Case

class TestAIProcessors(unittest.TestCase):
    def test_response_model_factory(self):
        cases = [
            Case(
                call=ResponseModelFactory().make_overview().model_fields.keys,
                outp={'title':"", 'provider':"", 'description':"", 'link':"", 'subject':"", 'tags':""}.keys()
                )
        ]

        for case in cases:
            self.assertTrue(case.test())

unittest.main()