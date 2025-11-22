
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing_extensions import Self
from dataclasses import dataclass

from src.models import SchemaModelFactory
from src.models import Fields

@dataclass
class ChatPromptTemplateBuilder:
    "Builds a `ChatPromptTemplate` object after adding a parser, instructions, and query"

    parser: PydanticOutputParser = None
    instructions: str = None
    query: str = None

    def _create_parser_from_str(self, target_info:str, factory:SchemaModelFactory=None):
        factory = factory or SchemaModelFactory()
        # The factory returns the specified section class 
        # which is then passed into the output parser constructor
        self.parser = PydanticOutputParser(pydantic_object=factory.make(target_info))

    def add_parser(self, target_info:str|Fields, factory:SchemaModelFactory=None) -> Self:
        "Adds a `BaseModel` parser to be added to the `ChatPromptTemplate`"
        if isinstance(target_info, Fields):
            target_info = target_info.value
        
        self._create_parser_from_str(target_info, factory=factory)

        return self

    def add_instructions(self, instructions:str) -> Self:
        "Adds the string system instructions to be added to the `ChatPromptTemplate`"
        if not isinstance(instructions, str):
            raise TypeError("instructions should be a string")
        self.instructions = instructions
        return self
    
    def add_query(self, query:str) -> Self:
        "Adds a string query to be added to the `ChatPromptTemplate`"
        if not isinstance(query, str):
            raise TypeError("query should be a string")
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

        self.chat_prompt_template = prompt_obj
    
    def get_chat_prompt_template(self) -> ChatPromptTemplate:
        """Returns the `ChatPromptTemplate` object created by the builder
        or builds it and then returns it if it hasn't been built yet"""

        missing = []
        if self.parser is None: missing.append("parser")
        if self.instructions is None: missing.append("instructions")
        if self.query is None: missing.append("query")

        if missing:
            raise TypeError(f"The following parameters are missing: {missing}")
        
        if not hasattr(self, "chat_prompt_template"):
            self._create_chat_prompt_template()

        return self.chat_prompt_template