
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, ConfigDict
from typing import List, Self, Optional

from src.models import Queue
from src.features.ai_processors import azure_chat_openai
from src.logging import Logger

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

class ResponseModel(BaseModelConfig):
    new_queue: List[str] = ["placeholder"]

INSTRUCTIONS = """
You are given a dictionary after the line: QUEUE HERE.
You are also given a partially filled JSON schema after PROGRAM INFO.
The dictionary represents a queue to go through links for web crawling purposes needed to find information to completely fill the partially filled JSON schema.
Your job is to go through the the link contents (key) and the URLs (value) and remove all the links that likely wouldn't contain the needed information.
You will send the dictionary back which will be parsed into a dictionary that will represent the links that likely have information related to the program in the partially filled JSON schema.

Core rules:
- If a link looks like it points to the admissions for a university, and not the program, it can be removed.
- If a link leads to any links similar to a:
  1. Google Drive
  2. Video (Youtube, Vimeo, etc.)
  3. PDF
  4. Completely unrelated website (unless it is a Google Form)
  It can be removed.

Don't add any links and be very conservative with the link removing process. 
Don't be afraid to remove every link from the queue if it's obvious none of them are needed, in that case return an empty dictionary.
"""

class AIQueueFilter:
    def __init__(self, log: Optional[Logger]=None) -> None:
        self.log = log or Logger(enabled=False)

        self.parser = PydanticOutputParser(pydantic_object=ResponseModel)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    {instructions}
                    Wrap the output in this format and provide no other text\n{format_instructions}
                    """,
                ),
                ("human", "{query}"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions(), instructions=INSTRUCTIONS)

    def add_queue(self, queue:Queue) -> Self:
        self.prompt = self.prompt.partial(query=queue.get_all_urls())
        return self

    def _parse_response(self, response) -> ResponseModel:
        try:
            parsed_response = self.parser.parse(response.content)
            return parsed_response
        
        except Exception as e:
            raise e

    def invoke(self, model=azure_chat_openai) -> ResponseModel:
        "Invokes the model to filter the given queue"
        prompt_value = self.prompt.format_prompt()

        response = model.invoke(prompt_value)
        parsed_response = self._parse_response(response)
        return parsed_response
    
if __name__ == "__main__":
    pass