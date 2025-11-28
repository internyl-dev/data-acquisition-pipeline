
import json

from langchain.output_parsers import PydanticOutputParser, ChatPromptValue, BaseMessage
from typing import Optional

from src.features.content_summarizers import ContentTrimmer
from src.features.logger import Logger
from src.features.ai_processors import azure_chat_openai
from src.features.schema_validators import SchemaValidationEngine
from .prompt_builder import PromptChainPromptBuilder, ChatPromptTemplate
from src.models import Fields, RootSchema, SchemaModelFactory

class PromptChainExecutor:
    """
    A prompt chain executor that when run, 
    first truncates the contents of a given webpage based on what information is being targetted,
    and second invokes the model over a loop that aims to collect all required target information. 

    Args:
        schema (dict | BaseSchemaSection): The schema in any state (populated or unpopulated)
        all_target_info (list[str | Fields]): The target information during the prompt chain
    """
    def __init__(
        self, 
        schema: RootSchema, 
        all_target_info: Optional[list[str|Fields]] = None, 
        validator: Optional[SchemaValidationEngine] = None, 
        trimmer: Optional[ContentTrimmer] = None, 
        factory: Optional[SchemaModelFactory] = None, 
        log: Optional[Logger] = None
        ) -> None:

        self.trimmer = trimmer or ContentTrimmer()
        self.factory = factory or SchemaModelFactory()
        self.log = log or Logger(log_mode=False)
        self.validator = validator or SchemaValidationEngine(return_str=True)

        self.schema = schema
        self.all_target_info = all_target_info or self.validator.validate_all(self.schema)
        self.prompt_builder = PromptChainPromptBuilder(schema)
    
    def _all_info_needed(self, target_info:list) -> bool:
        "The clause for when to activate bulk extraction"
        return len(target_info) == 6
    
    def _build_prompt(self, target_info:str, contents:str) -> ChatPromptTemplate:
        "Builds the prompt to pass into the chat model"
        return self.prompt_builder.build(target_info, contents)

    def run(self, contents:str) -> RootSchema:
        """Loops through the target info at each iteration 
        makeing a prompt object, passing it into a chat, 
        invoking the chat, and updating the current schema"""

        self.log.update(f"PROMPT EXECUTOR: Executing prompt chain for the following info: {self.all_target_info}")

        for target_info in self.all_target_info:
            self.log.update(f"PROMPT EXECUTOR: Creating prompt for {target_info}")

            if self._all_info_needed(self.all_target_info):
                self.log.update("PROMPT EXECUTOR: Ignore previous log, bulk extraction activated. Creating prompt for ALL")
                target_info = "all"
            
            trimmed_contents: str = self.trimmer.truncate_contents(contents, target_info, 500, 1)
            self.log.update(trimmed_contents)

            prompt: ChatPromptTemplate = self._build_prompt(target_info, trimmed_contents)
            #self.log.update(prompt.partial_variables)
            parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=self.factory.make(target_info))
            prompt_value: ChatPromptValue = prompt.format_prompt()

            self.log.update("PROMPT EXECUTOR: Sending request...")
            response: BaseMessage = azure_chat_openai.invoke(prompt_value)
            self.log.update(json.loads(response.content))

            try:
                parsed_schema = parser.parse(response.content)
                self.log.update("PROMPT EXECUTOR: Successfully parsed to schema object")
                #self.log.update(parsed_schema)
            
            except Exception as e:
                self.log.update(f"PROMPT EXECUTOR: Parsing error: {e}")
                response_dict = json.loads(response.content)
                self.log.update(response_dict)
                raise e
            
            if len(self.all_target_info) == 6:
                self.schema = parsed_schema
                break
            else:
                if target_info == Fields.OVERVIEW:
                    self.schema.overview = parsed_schema
                if target_info == Fields.ELIGIBILITY:
                    self.schema.eligibility = parsed_schema
                if target_info == Fields.DATES:
                    self.schema.dates = parsed_schema
                if target_info == Fields.COSTS:
                    self.schema.costs = parsed_schema
                if target_info == Fields.CONTACT:
                    self.schema.contact = parsed_schema

        return self.schema
    
    
if __name__ == "__main__":
    #chain = PromptChainExecutor()
    print("need thing")