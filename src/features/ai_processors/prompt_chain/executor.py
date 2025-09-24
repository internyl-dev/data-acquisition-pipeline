
import json

from langchain.output_parsers import PydanticOutputParser 

from src.features.content_summarizers import ContentTrimmer
from src.features.logger import Logger
from src.features.ai_processors import azure_chat_openai, create_chat_prompt_template
from src.features.schema_validators import SchemaValidationEngine
from .prompt_builder import PromptChainPromptBuilder
from src.models import Fields, BaseSchemaSection, SchemaModelFactory

class PromptChainExecutor:
    """
    A prompt chain executor that when run, 
    first truncates the contents of a given webpage based on what information is being targetted,
    and second invokes the model over a loop that aims to collect all required target information. 

    Args:
        schema (dict | BaseSchemaSection): The schema in any state (populated or unpopulated)
        all_target_info (list[str | Fields]): The target information during the prompt chain
    """
    def __init__(self, 
                 schema: dict|BaseSchemaSection, 
                 all_target_info:list[str|Fields]=None, 
                 validator=None, trimmer=None, factory=None, log=None):
        self.trimmer = trimmer or ContentTrimmer()
        self.factory = factory or SchemaModelFactory()
        self.log = log or Logger(log_mode=False)
        self.validator = validator or SchemaValidationEngine()

        self.schema = schema
        self.all_target_info = all_target_info or validator.validate_all()
        self.prompt_builder = PromptChainPromptBuilder(schema)
    
    def _all_info_needed(self, target_info) -> bool:
        "The clause for when to activate bulk extraction"
        return len(target_info) == 6
    
    def _build_prompt(self, target_info, contents):
        "Builds the prompt to pass into the chat model"
        return self.prompt_builder.build(target_info, contents)

    def run(self, contents) -> BaseSchemaSection:
        """Loops through the target info at each iteration 
        makeing a prompt object, passing it into a chat, 
        invoking the chat, and updating the current schema"""
        self.log.update(f"PROMPT EXECUTOR: Executing prompt chain for the following info: {self.all_target_info}")
        for target_info in self.all_target_info:
            self.log.update(f"PROMPT EXECUTOR: Creating prompt for {target_info}")

            if self._all_info_needed(self.all_target_info):
                self.log.update("PROMPT EXECUTOR: Ignore previous log, bulk extraction activated. Creating prompt for ALL")
                target_info = "all"
            
            trimmed_contents = self.trimmer.truncate_contents(contents, target_info, 500, 1)

            prompt = self._build_prompt(target_info, trimmed_contents)
            parser = PydanticOutputParser(pydantic_object=self.factory.make(target_info))
            prompt_value = prompt.format_prompt()

            self.log.update("PROMPT EXECUTOR: Sending request...")
            response = azure_chat_openai.invoke(prompt_value)
            self.log.update(json.loads(response.content))

            try:
                parsed_schema = parser.parse(response.content)
                self.log.update("PROMPT EXECUTOR: Successfully parsed to schema object")
                self.log.update(parsed_schema)
            
            except Exception as e:
                self.log.update(f"PROMPT EXECUTOR: Parsing error: {e}")
                response_dict = json.loads(response.content)
                self.log.update(response_dict)
            
            if len(self.all_target_info) == 6:
                self.schema = parsed_schema
                break
            else:
                if target_info == Fields.OVERVIEW:
                    self.overview = parsed_schema
                if target_info == Fields.ELIGIBILITY:
                    self.eligibility = parsed_schema
                if target_info == Fields.DATES:
                    self.dates = parsed_schema
                if target_info == Fields.COSTS:
                    self.costs = parsed_schema
                if target_info == Fields.CONTACT:
                    self.contact = parsed_schema
        return self.schema
    
    
if __name__ == "__main__":
    chain = PromptChainExecutor()