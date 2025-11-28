
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Self, Optional
from dataclasses import dataclass

from src.models import SchemaModelFactory
from src.models import Fields

@dataclass
class ChatPromptTemplateBuilder:
    "Builds a `ChatPromptTemplate` object after adding a parser, instructions, and query"

    parser: Optional[PydanticOutputParser] = None
    instructions: Optional[str] = None
    query: Optional[str] = None

    def _create_parser_from_str(self, target_info:str, factory: Optional[SchemaModelFactory] = None) -> None:
        "Sets instance parser variable"
        # The factory returns the specified section class 
        # which is then passed into the output parser constructor
        factory = factory or SchemaModelFactory()
        
        self.parser = PydanticOutputParser(pydantic_object=factory.make(target_info))

    def add_parser(self, target_info:str|Fields, factory: Optional[SchemaModelFactory] = None) -> Self:
        "Adds a `BaseModel` parser to be added to the `ChatPromptTemplate`"
        if isinstance(target_info, Fields):
            target_info = target_info.value
        
        self._create_parser_from_str(target_info, factory=factory)

        return self

    def add_instructions(self, instructions:str) -> Self:
        "Adds the string system instructions to be added to the `ChatPromptTemplate`"
        self.instructions = instructions
        return self
    
    def add_query(self, query:str) -> Self:
        "Adds a string query to be added to the `ChatPromptTemplate`"
        
        self.query = query
        return self

    def _create_chat_prompt_template(self) -> None:
        "Creates a `ChatPromptTemplate` using the components given to itself"
        if self.parser is None: raise TypeError("The parser hasn't been added yet, cannot get format instructions")
        prompt_obj: ChatPromptTemplate = ChatPromptTemplate.from_messages(
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

        missing: list[str] = []
        if self.parser is None: missing.append("parser")
        if self.instructions is None: missing.append("instructions")
        if self.query is None: missing.append("query")

        if missing:
            raise TypeError(f"The following parameters are missing: {missing}")
        
        if not hasattr(self, "chat_prompt_template"):
            self._create_chat_prompt_template()

        return self.chat_prompt_template