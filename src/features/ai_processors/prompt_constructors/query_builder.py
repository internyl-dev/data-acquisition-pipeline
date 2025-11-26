
import json
from typing import Self

class Query:
    def __init__(self):
        self.prompt_architecture = {
            "schema_context": [],
            "program_context": [],
            "webpage_contents": []
        }

    def add_schema_context(self, schema:str|dict) -> None:
        "Adds the schema as context to be used by the model"
        if isinstance(schema, dict):
            schema = json.dumps(schema)
        elif not isinstance(schema, str):
            raise TypeError(f"`schema` should be a string, got {type(schema)}")
        
        self.prompt_architecture["schema_context"].append(schema)

    def add_program_context(self, s:str) -> None:
        "Adds information about the program to be used as context by the model"
        if not isinstance(s, str):
            raise TypeError(f"`s` should be a string, got {type(s)}")
        self.prompt_architecture["program_context"].append(s)

    def add_webpage_contents(self, s:str) -> None:
        "Adds the contents of a webpage to be used to find new information"
        if not isinstance(s, str):
            raise TypeError(f"`s` should be a string, got {type(s)}")
        self.prompt_architecture["webpage_contents"].append(s)

    def get_prompt(self) -> str:
        "Returns the entire query as a string"
        prompt = []
        for key in self.prompt_architecture:
            prompt.append('\n'.join(self.prompt_architecture[key]))

        return '\n'.join(prompt)

class QueryBuilder:
    """
    Builds a `Query` object by adding components\n
    Using the `get_prompt` method in a `Query` object, 
    you can get the string representation of the query you built
    and pass that string into a `ChatPromptTemplateBuilder`
    """
    def __init__(self, prompt_obj:Query=None):
        self.prompt_obj = prompt_obj or Query()
        self.schema_context = self.prompt_obj.prompt_architecture["schema_context"]
        self.program_context = self.prompt_obj.prompt_architecture["program_context"]
        self.webpage_contents = self.prompt_obj.prompt_architecture["webpage_contents"]

    def _add_schema_context_boiler(self) -> None:
        "This text helps the model find where the schema context is in a query"
        self.prompt_obj.add_schema_context("ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA:")

    def _add_program_context_boiler(self) -> None:
        "This text helps the model find where the program context is in a query"
        self.prompt_obj.add_program_context("TARGET PROGRAM INFORMATION:")

    def _add_webpage_contents_boiler(self) -> None:
        "This text helps the model find where the webpage contents are in a query"
        self.prompt_obj.add_webpage_contents("WEBPAGE CONTENTS START HERE:")

    def add_schema_context(self, context:str) -> Self:
        if not isinstance(context, str):
            raise TypeError(f"`context` should be a string, got {type(context)}")
        
        if not self.schema_context:
            self._add_schema_context_boiler()

        self.prompt_obj.add_schema_context(context)
        return self
        
    def add_title(self, title:str) -> Self:
        if not isinstance(title, str):
            raise TypeError(f"`title` should be a string, got {type(title)}")
        
        if not self.program_context:
            self._add_program_context_boiler()

        self.prompt_obj.add_program_context(f"Title: {title}")
        return self

    def add_provider(self, provider:str) -> Self:
        if not isinstance(provider, str):
            raise TypeError(f"`provider` should be a string, got {type(provider)}")
        
        if not self.program_context:
            self._add_program_context_boiler()

        self.prompt_obj.add_program_context(f"Provider: {provider}")
        return self

    def add_description(self, description:str) -> Self:
        if not isinstance(description, str):
            raise TypeError(f"`description` should be a string, got {type(description)}")

        if not self.program_context:
            self._add_program_context_boiler()

        self.prompt_obj.add_program_context(f"Description: {description}")
        return self
    
    def add_webpage_contents(self, contents:str) -> Self:
        "Adds the webpage contents for the model to collect data from"
        if not isinstance(contents, str):
            raise TypeError(f"`contents` should be a string, got {type(contents)}")
        
        if not self.webpage_contents:
            # The below method calls another method that sets the webpage_contents instance variable
            self._add_webpage_contents_boiler()
        self.prompt_obj.add_webpage_contents(contents)
        return self
    
    def get_prompt_obj(self) -> Query:
        return self.prompt_obj