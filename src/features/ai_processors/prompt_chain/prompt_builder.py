
from ..prompt_constructors import SystemInstructionsBuilder, QueryBuilder, ChatPromptTemplateBuilder, ChatPromptTemplate

from src.models import BaseSchemaSection, Fields

class PromptChainPromptBuilder:
    """
    The builder object for the `ChatPromptTemplate` object to be passed into a chat
    and invoked\n
    The builder automatically makes the system instructions and query based on the
    current state of the schema or the required information passed into it

    Args:
        schema (dict | BaseSchemaSection): The schema which will be used to get all target
        info
        all_target_info (list[str | Fields]): The information for the model to find
        which will be included in the query
    """
    def __init__(self, schema: dict | BaseSchemaSection):

        self.schema = schema

    def _build_system_instructions(self, target_info:str|Fields) -> str:
        "Automatically constructs the system instructions given some target info"
        builder = SystemInstructionsBuilder()
        builder.add_instructions(target_info)
        instructions_obj = builder.get_obj()

        return instructions_obj.get_instructions()

    def _legacy_build_query(self, contents) -> str:
        "Automatically constructs the query given the dictionary schema and some webpage contents"
        builder = QueryBuilder()
        builder.add_schema_context(self.schema) \
               .add_title(self.schema["overview"]["title"]) \
               .add_description(self.schema["overview"]["description"]) \
               .add_provider(self.schema["overview"]["provider"]) \
               .add_webpage_contents(contents)
        query_obj = builder.get_prompt_obj()

        return query_obj.get_prompt()
    
    def _build_query(self, contents) -> str:
        "Automatically constructs the query given the BaseSchemaSection schema and some webpage contents"
        builder = QueryBuilder()
        builder.add_schema_context(self.schema) \
               .add_title(self.schema.overview.title) \
               .add_description(self.schema.overview.description) \
               .add_provider(self.schema.overview.provider) \
               .add_webpage_contents(contents)
        query_obj = builder.get_prompt_obj()

        return query_obj
    
    def _build_prompt(self, target_info, instructions, query) -> ChatPromptTemplate:
        """Automatically constructs a `ChatPromptTemplate` object 
        given the system instructions and a query as strings"""
        builder = ChatPromptTemplateBuilder()
        builder.add_parser(target_info) \
               .add_instructions(instructions) \
               .add_query(query)
        prompt_obj = builder.get_chat_prompt_template()

        return prompt_obj
    
    def build(self, target_info: str|Fields, contents:str) -> ChatPromptTemplate:
        """
        Automatically builds a prompt given the target information
        and some contents\n
        The method automatically chooses between legacy builders
        and modern builders based on the parameter types

        Args:
            target_info (str | Fields): The target fields to prompt the model to extract
            contents (str): The contents to extract information from

        Returns:
            prompt (ChatPromptTemplate): The object with which to pass as an argument into
            a chat object when invoking it
        """
        if isinstance(self.schema, BaseSchemaSection):
            build_query = self._build_query
        elif isinstance(self.schema, dict):
            build_query = self._legacy_build_query
            
        instructions = self._build_system_instructions(target_info)
        query = build_query(contents)
        prompt = self._build_prompt(target_info, instructions, query)

        return prompt