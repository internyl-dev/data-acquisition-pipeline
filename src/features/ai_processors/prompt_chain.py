
import json

from src.features.schema_validators import SchemaValidationEngine
from src.features.content_summarizers import ContentTrimmer
from src.features.logger import Logger
from .azure_client import azure_chat_openai, create_chat_prompt_template
from .prompt_constructors import SystemInstructionsBuilder, QueryBuilder, ChatPromptTemplateBuilder

class PromptChain:
    def __init__(self, schema, all_target_info=None, validator=None, trimmer=None, log=None):
        self.validator = validator or SchemaValidationEngine()
        self.trimmer = trimmer or ContentTrimmer()
        self.log = log or Logger()

        self.schema = schema
        self.all_target_info = all_target_info or SchemaValidationEngine().validate_all()


    def _build_system_instructions(self, target_info):
        builder = SystemInstructionsBuilder()
        builder.add_instructions(target_info)
        instructions_obj = builder.get_obj()

        return instructions_obj.get_instructions()

    def _legacy_build_query(self, contents):
        builder = QueryBuilder()
        builder.add_schema_context(self.schema) \
               .add_title(self.schema["overview"]["title"]) \
               .add_description(self.schema["overview"]["description"]) \
               .add_provider(self.schema["overview"]["provider"]) \
               .add_webpage_contents(contents)
        query_obj = builder.get_prompt_obj()

        return query_obj.get_prompt()
    
    def _build_query(self, contents):
        builder = QueryBuilder()
        builder.add_schema_context(self.schema) \
               .add_title(self.schema.overview.title) \
               .add_description(self.schema.overview.description) \
               .add_provider(self.schema.overview.provider) \
               .add_webpage_contents(contents)
        query_obj = builder.get_prompt_obj()

        return query_obj
    
    def _build_prompt(self, target_info, instructions, query):
        builder = ChatPromptTemplateBuilder()
        builder.add_parser(target_info) \
               .add_instructions(instructions) \
               .add_query(query)
        prompt_obj = builder.get_chat_prompt_template()

        return prompt_obj
    
    def _all_info_needed(self, target_info):
        return len(target_info) == 6

    def legacy_run(self, contents):
        for target_info in self.all_target_info:

            if self._all_info_needed:
                target_info = "all"
            
            trimmed_contents = self.trimmer.truncate_contents(contents, target_info, 500, 1)

            instructions = self._build_system_instructions(target_info)
            query = self._build_query(trimmed_contents)
            prompt = self._build_prompt(target_info, instructions, query)

            self.log.update("Sending request...")
            response = azure_chat_openai.invoke(prompt)

            response_dict = json.loads(response.model_dump()["content"])
            self.log.update(response_dict)
            
            if len(self.all_target_info) == 6:
                self.schema = response_dict
                break
            else:
                self.schema[target_info] = response_dict
                continue
        
        return self.schema
    
if __name__ == "__main__":
    chain = PromptChain()