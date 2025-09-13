
import json

class Query:
    def __init__(self):
        self.prompt_architecture = {
            "schema_context": [],
            "program_context": [],
            "webpage_contents": []
        }

    def add_schema_context(self, schema:str|dict):
        if isinstance(schema, dict):
            schema = json.dumps(schema)
        self.prompt_architecture["schema_context"].append(schema)

    def add_program_context(self, s:str):
        self.prompt_architecture["program_context"].append(s)

    def add_webpage_contents(self, s:str):
        self.prompt_architecture["webpage_contents"].append(s)

    def get_prompt(self):
        prompt = ""
        for key in self.prompt_architecture:
            prompt += '\n'.join(self.prompt_architecture[key])

        return prompt

class QueryBuilder:
    def __init__(self, prompt_obj=None):
        self.prompt_obj = prompt_obj or Query()
        self.schema_context = self.prompt_obj.prompt_architecture["schema_context"]
        self.program_context = self.prompt_obj.prompt_architecture["program_context"]
        self.webpage_contents = self.prompt_obj.prompt_architecture["webpage_contents"]

    def _add_schema_context_boiler(self):
        self.prompt_obj.add_schema_context("ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA:")

    def _add_program_context_boiler(self):
        self.prompt_obj.add_program_context("TARGET PROGRAM INFORMATION:")

    def _add_webpage_contents_boiler(self):
        self.prompt_obj.add_webpage_contents("WEBPAGE CONTENTS START HERE:")

    def add_schema_context(self, context:str):
        if not self.schema_context:
            self._add_schema_context_boiler()

        self.prompt_obj.add_schema_context(context)
        return self
        
    def add_title(self, title:str):
        if not self.program_context:
            self._add_program_context_boiler()

        self.prompt_obj.add_program_context(f"Title: {title}")
        return self

    def add_provider(self, provider:str):
        if not self.program_context:
            self._add_program_context_boiler()

        self.prompt_obj.add_program_context(f"Provider: {provider}")
        return self

    def add_description(self, description:str):
        if not self.program_context:
            self._add_program_context_boiler()

        self.prompt_obj.add_program_context(f"Description: {description}")
        return self
    
    def add_webpage_contents(self, contents:str):
        self.prompt_obj.add_webpage_contents(contents)
        return self
    
    def get_prompt_obj(self):
        return self.prompt_obj