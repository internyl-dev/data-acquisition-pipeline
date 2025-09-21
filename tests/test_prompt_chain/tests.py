
import unittest

from src.features.ai_processors.prompt_constructors import QueryBuilder, SystemInstructionsBuilder, ChatPromptTemplateBuilder
from src.features.ai_processors.prompt_chain import PromptChainPromptBuilder
from src.features.ai_processors.prompt_constructors.instructions import INSTRUCTIONS
from src.models import Case, Fields, RootSchema, SchemaModelFactory

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

    def test_system_instructions_builder(self):
        cases = [
            Case(
                call=SystemInstructionsBuilder().add_instructions(Fields.CONTACT).get_obj().get_instructions,
                outp=INSTRUCTIONS["contact"]
            ),
            Case(
                call=SystemInstructionsBuilder().add_instructions("contact").get_obj().get_instructions,
                outp=INSTRUCTIONS["contact"]
            )
        ]

        for case in cases:
            self.assertTrue(
                case.test()
            )

    def test_cpt_builder(self):
        query = QueryBuilder().add_schema_context({"schema": "test"}) \
                              .add_title("title") \
                              .add_description("description") \
                              .add_provider("provider") \
                              .add_webpage_contents("webp contents") \
                              .get_prompt_obj().get_prompt()
        
        instructions = SystemInstructionsBuilder().add_instructions(Fields.OVERVIEW) \
                                                  .get_obj().get_instructions()
        
        cpt = ChatPromptTemplateBuilder().add_query(query) \
                                         .add_instructions(instructions) \
                                         .add_parser(Fields.OVERVIEW) \
                                         .get_chat_prompt_template()
        
        #print("Partial variables:\n\n", cpt.partial_variables)

    def test_prompt_builder(self):
        example_schema = {
            "overview": {
                "title": "TITLE",
                "description": "DESCRIPTION",
                "provider": "PROVIDER"
            }
        }
        
        example_webp_cont = "WEBPAGE CONTENTS"
        
        cpt = PromptChainPromptBuilder(example_schema, Fields.OVERVIEW).build(Fields.OVERVIEW, example_webp_cont)

        print(cpt.partial_variables)

unittest.main()