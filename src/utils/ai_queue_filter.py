
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, ConfigDict
from typing import List

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

class ResponseModel(BaseModelConfig):
    new_queue: List[str]

INSTRUCTIONS = ""

class AIQueueFilter:
    def __init__(self):
        parser = PydanticOutputParser(pydantic_object=ResponseModel)
        prompt = ChatPromptTemplate.from_messages(
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
        ).partial(format_instructions=parser.get_format_instructions(), instructions=INSTRUCTIONS)
    