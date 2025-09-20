
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from src.models import SchemaModelFactory
from src.models import Fields
from .prompt_constructors.instructions import INSTRUCTIONS


load_dotenv()

azure_chat_openai = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_MODEL"),
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

def create_chat_prompt_template(required_info:str|Fields, factory=None):
    "Creates a `ChatPromptTemplate` object that which can be placed into a chat object when it is invoked"
    factory = factory or SchemaModelFactory()
    model = factory.make(required_info)
    parser = PydanticOutputParser(pydantic_object=model)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                {instructions}
                Wrap the output in this format and provide no other text\n{format_instructions}
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions(), instructions=INSTRUCTIONS[required_info])

    return prompt