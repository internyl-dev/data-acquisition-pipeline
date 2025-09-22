
import json

from src.features.content_summarizers import ContentTrimmer
from src.features.logger import Logger
from src.features.ai_processors import azure_chat_openai, create_chat_prompt_template
from .prompt_builder import PromptChainPromptBuilder

from src.models import Fields
from src.models import BaseSchemaSection

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
                 validator=None, trimmer=None, log=None):
        self.trimmer = trimmer or ContentTrimmer()
        self.log = log or Logger()

        self.schema = schema

        self.prompt_builder = PromptChainPromptBuilder(schema, all_target_info)
    
    def _all_info_needed(self, target_info) -> bool:
        "The clause for when to activate bulk extraction"
        return len(target_info) == 6

    def run(self, contents) -> BaseSchemaSection:
        """Loops through the target info at each iteration 
        makeing a prompt object, passing it into a chat, 
        invoking the chat, and updating the current schema"""
        for target_info in self.all_target_info:

            if self._all_info_needed:
                # Bulk extraction activated
                target_info = "all"
            
            trimmed_contents = self.trimmer.truncate_contents(contents, target_info, 500, 1)

            prompt = self.prompt_builder.build(target_info, trimmed_contents)

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
    chain = PromptChainExecutor()