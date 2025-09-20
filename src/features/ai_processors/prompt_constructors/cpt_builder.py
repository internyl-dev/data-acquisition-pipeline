
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.models import SchemaModelFactory
from src.models import Fields

class ChatPromptTemplateBuilder:
    def add_parser(self, required_info:str|Fields, factory=None):
        factory = factory or SchemaModelFactory()
        self.parser = factory.make(required_info)
        return self

    def add_instructions(self, instructions:str):
        self.instructions = instructions
        return self
    
    def add_query(self, query):
        self.query = query
        return self

    def _create_chat_prompt_template(self):
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

        return prompt_obj
    
    def get_chat_prompt_template(self):
        return self._create_chat_prompt_template()