
import json

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.messages.base import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional

from src.features.content_summarizers import ContentTrimmer
from src.logging import Logger
from src.features.ai_processors import azure_chat_openai
from src.features.schema_validators import SchemaValidationEngine
from .prompt_builder import PromptChainPromptBuilder
from src.models import Fields, RootSchema, SchemaModelFactory
from src.models.schema_models import Overview, \
                                     Eligibility, \
                                     Dates, \
                                     Locations, \
                                     Costs, \
                                     Contact \

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
        all_target_info: Optional[list[str] | list[Fields]] = None, 
        validator: Optional[SchemaValidationEngine] = None, 
        trimmer: Optional[ContentTrimmer] = None, 
        factory: Optional[SchemaModelFactory] = None, 
        log: Optional[Logger] = None
        ) -> None:

        self.trimmer = trimmer or ContentTrimmer()
        self.factory = factory or SchemaModelFactory()
        self.log = log or Logger(enabled=False)
        self.validator = validator or SchemaValidationEngine()

        self.schema = schema
        self.all_target_info = all_target_info or self.validator.validate_all(self.schema, return_str=True)
        self.prompt_builder = PromptChainPromptBuilder(schema)
    
    @staticmethod
    def _all_info_needed(target_info:list) -> bool:
        "The clause for when to activate bulk extraction"
        return len(target_info) == 6
    
    def _build_prompt(self, target_info:str, contents:str) -> ChatPromptTemplate:
        "Builds the prompt to pass into the chat model"
        return self.prompt_builder.build(target_info, contents)

    @staticmethod
    def __get_token_counts(response:BaseMessage) -> tuple[int, int]:
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            usage = response.response_metadata['token_usage']
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
        
            return prompt_tokens, completion_tokens
        return 0, 0

    def _update_metadata(self, response) -> None:
        prompt_tokens, completion_tokens = self.__get_token_counts(response)
        self.schema.metadata.total_input_tokens+=prompt_tokens
        self.schema.metadata.total_output_tokens+=completion_tokens
            
    def run(self, contents:str) -> RootSchema:
        """Loops through the target info at each iteration 
        makeing a prompt object, passing it into a chat, 
        invoking the chat, and updating the current schema"""

        self.log.update(f"PROMPT EXECUTOR: Executing prompt chain for the following info: {self.all_target_info}")

        for _target_info in self.all_target_info:
            if isinstance(_target_info, Fields):
                target_info: str = _target_info.value
            else:
                target_info: str = _target_info

            self.log.update(f"PROMPT EXECUTOR: Creating prompt for {target_info}")

            if self._all_info_needed(self.all_target_info):
                self.log.update("PROMPT EXECUTOR: Overriden, bulk extraction activated. Creating prompt for ALL")
                target_info = "all"
            
            trimmed_contents: str = self.trimmer.truncate_contents(contents, target_info, 500, 1)
            self.log.update(trimmed_contents)

            prompt: ChatPromptTemplate = self._build_prompt(target_info, trimmed_contents)
            #self.log.update(prompt.partial_variables)
            parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=self.factory.make(target_info))
            prompt_value: ChatPromptValue = prompt.format_prompt()

            self.log.update("PROMPT EXECUTOR: Sending request...")
            response: BaseMessage = azure_chat_openai.invoke(prompt_value)
            raw_content = response.content

            # Add token counts
            self._update_metadata(response)

            content_str = self._normalize_response(raw_content)
            parsed_schema = self._parse_response(parser, content_str)

            if isinstance(parsed_schema, RootSchema):
                self.schema = parsed_schema
                break
            else:
                self._update_schema_section(parsed_schema)

        return self.schema

    def _normalize_response(self, raw_content) -> str:
        # Normalize response.content -> string
        if isinstance(raw_content, str):
            content_str = raw_content
        else:
            # Convert parts (list) to a single text string
            content_str = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in raw_content
            )

        self.log.update_api(content_str)
        return content_str

    def _parse_response(self, parser: PydanticOutputParser, content_str: str) -> Contact | Costs | Dates | Eligibility | Locations | Overview | RootSchema:
        try:
            parsed_schema = parser.parse(content_str)
            self.log.update("PROMPT EXECUTOR: Successfully parsed to schema object")
            self.log.update_api(parsed_schema)
            return parsed_schema
        
        except Exception as e:
            self.log.update(f"PROMPT EXECUTOR: Parsing error: {e}", level=self.log.ERROR)
            response_dict = json.loads(content_str)
            self.log.update_api(response_dict)
            raise e

    def _update_schema_section(self, parsed_schema) -> None:
        match parsed_schema:
            case Overview():
                self.schema.overview = parsed_schema
            case Eligibility():
                self.schema.eligibility = parsed_schema
            case Dates():
                self.schema.dates = parsed_schema
            case Locations():
                self.schema.locations = parsed_schema
            case Costs():
                self.schema.costs = parsed_schema
            case Contact():
                self.schema.contact = parsed_schema
    

if __name__ == "__main__":
    #chain = PromptChainExecutor()
    print("need thing")