
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
import json
from src.components.lib.prompts import prompts

from dotenv import load_dotenv
import os
load_dotenv()

class Client:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

        SCHEMA_FILE_PATH = "src/components/lib/schemas.json"
        with open(SCHEMA_FILE_PATH, 'r', encoding='utf-8') as file:
            self.response = json.load(file)

        self.prompts = prompts

    def create_prompt(self, contents:BeautifulSoup|str, required_info:str):
        """
        Creates the context for the language model to extract necessary info from.

        Args:
            contents (BeautifulSoup | str): Contains the contents of the webpage
            required_info (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)
        
        Returns:
            value (str): Truncated contents of the webpage and a portion of the 'overview' schema 
            including the required info that the model needs to scrape
        """
        # Create the context for the language model
        # Includes the information about the target internship
        # L> Helps model determine if the web page is the same internship
        # Include target information needed for extraction
        if required_info == "all":
            schema = str(self.response)
        else:
            schema = str({required_info: self.response[required_info]})

        return (
            '\nADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA: '
            + schema + '\n'
            + '\nTARGET INTERNSHIP INFORMATION: '
            + 'Title: ' + self.response['overview']['title'] + '\n'
            + 'Provider: ' + self.response['overview']['provider'] + '\n'
            + 'Description: ' + self.response['overview']['description'] + '\n'
            + '\nWEBPAGE CONTENTS START HERE: '
            + self.truncate_contents(contents, required_info)
            )

    def post_openrouter(self, prompt:str, model:str="google/gemma-3n-e2b-it:free"):
        """
        Sends post request to the OpenRouter completions server

        Args:
            prompt (str): The prompt to send to the model
            model (str): The name of the model to use

        Returns:
            output (str): Output from model given prompt
        """
        api_key = self.openrouter_api_key
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        json={
            "model": model,
            "messages": [
                { "role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(url, headers, json)
        return response
    
    def post_openai(self, prompt:str, context:str="You are a helpful assistant", model:str="gpt-4o-mini"):
        """
        Sends post request to the OpenAI completions server

        Args:
            prompt (str): The prompt to send to the model
            model (str): The name of the model to use

        Returns:
            output (str): Output from model given prompt
        """
        client = OpenAI(
        api_key=self.openai_api_key
        )

        completion = client.chat.completions.create(
        model=model,
        store=True,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ]
        )

        print(completion.choices[0].message)

    def validate_output(self, output):
        """
        """
        if output == {'unrelated_website': True}:
            pass

        error = ''

        output_keys = list(output.keys())
        output_key = output_keys[0]

        if len(output_keys) > 1:
            error += f'ERROR: multiple categories detected; {len(output_keys)} categories: {output_keys}\n'
            error += f'Moving on to first category: {output_key}\n'

        categories = list(self.response.keys())
        if output_key not in categories:
            return f'ERROR: invalid schema output; {output_key} is an invalid category\n'
        
        output_sections = list(output[output_key].keys())
        schema_sections = list(self.response[output_key].keys())

        # Get all sections in the output that are not in the schema (invalid sections)
        invalid_sections = list(set(output_sections) - set(schema_sections))
        
        if invalid_sections:
            if len(invalid_sections) > 1:
                error += f'ERROR: invalid schema output; {invalid_sections} are invalid sections\n'
            else:
                error += f'ERROR: invalid schema output; {invalid_sections} is an invalid section\n'

        # Get all sections in the schema that are not in the output (missing sections)
        missing_sections = list(set(schema_sections) - set(output_sections))

        if missing_sections:
            if len(invalid_sections) > 1:
                error += f'ERROR: invalid schema output; {missing_sections} are missing\n'
            else:
                error += f'ERROR: invalid schema output; {missing_sections} is missing\n'
        
        return error + str(output)

    def handle_output(self, response, required_info):
        """
        Takes the output from the model and makes it usable in the rest of the codebase.
        Args:
            response (str): The output from the model

        Returns:
            value (dict or None): The dictionary output from the model assuming it returned a dictionary 
            or None if the output isn't a dictionary or if the output is {"unrelated_website": True}
        """
        # Access the raw content string
        raw_content_string = response["choices"][0]["message"]["content"]

        # Remove the markdown code block delimiters if they exist
        # This is a common pattern for models returning structured data
        if raw_content_string.startswith("```json") and raw_content_string.endswith("```"):
            json_string = raw_content_string[len("```json"): -len("```")].strip()
        else:
            json_string = raw_content_string.strip() # In case it's just raw JSON without markdown

        # Parse the JSON string into a Python dictionary
        try:
            parsed_response = json.loads(json_string)
            print("Successfully parsed data:\n")
            print(json.dumps(parsed_response, indent=2))

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Problematic JSON string:\n{json_string}")
            return None
        except KeyError as e:
            print(f"Key error when accessing response: {e}. Check the structure of the response.")
            return None

        if parsed_response == {"unrelated_website": True}:
            return None

        # After parsing, update the initial schema

        # Update for non bulk_process requirements
        if not required_info == "all":
            self.response[required_info].update(parsed_response[required_info])

            return parsed_response
        
        # Update for bulk process requirements
        for category in self.response:
            for section in self.response[category]:
                # The parsed response doesn't contain the categories like "overview"
                # so we have to loop through each section in the schema and update it
                # with the corresponding section in the parsed response
                try:
                    self.response[category][section] = parsed_response[section]
                except Exception: continue

                return parsed_response