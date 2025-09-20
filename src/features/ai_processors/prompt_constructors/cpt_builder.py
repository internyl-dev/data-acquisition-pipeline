
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing_extensions import Self

from src.models import SchemaModelFactory
from src.models import Fields

class ChatPromptTemplateBuilder:
    "Builds a `ChatPromptTemplate` object"
    def add_parser(self, required_info:str|Fields, factory=None) -> Self:
        "Adds a `BaseModel` parser to be added to the `ChatPromptTemplate`"
        factory = factory or SchemaModelFactory()
        self.parser = factory.make(required_info)
        return self

    def add_instructions(self, instructions:str) -> Self:
        "Adds the string system instructions to be added to the `ChatPromptTemplate`"
        self.instructions = instructions
        return self
    
    def add_query(self, query) -> Self:
        "Adds a string query to be added to the `ChatPromptTemplate`"
        self.query = query
        return self

    def _create_chat_prompt_template(self) -> None:
        "Creates a `ChatPromptTemplate` using the components given to itself"
        prompt_obj = ChatPromptTemplate.from_messages(
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
        ).partial(format_instructions=self.parser.get_format_instructions(), 
                  instructions=self.instructions, 
                  query=self.query)

        self.chat_prompt_template =  prompt_obj
    
    def get_chat_prompt_template(self) -> ChatPromptTemplate:
        """Returns the `ChatPromptTemplate` object created by the builder
        or builds it and then returns it if it hasn't been built yet"""
        if not hasattr(self, "chat_prompt_template"):
            self._create_chat_prompt_template
        return self.chat_prompt_template