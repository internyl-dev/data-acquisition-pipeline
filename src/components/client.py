
from pprint import pprint
from bs4 import BeautifulSoup
import json
import requests
from openai import OpenAI
from src.components.lib.prompts import prompts

from dotenv import load_dotenv
import os
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")

CUSTOM_API_KEY = os.getenv("API_KEY")
CUSTOM_MODEL = os.getenv("MODEL")
CUSTOM_ENDPOINT_URL = os.getenv("ENDPOINT_URL")

class Client:
    def __init__(self):

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

    def post_openrouter(self, prompt:str, context:str="You are a helpful assisstant", model:str=OPENROUTER_MODEL):
        """
        Sends post request to the OpenRouter completions server

        Args:
            prompt (str): The prompt to send to the model
            model (str): The name of the model to use

        Returns:
            response (str): Output from model given prompt
        """
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        json={
            "model": model,
            "messages": [
                {"role": "system", "content": context},
                { "role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(url, headers, json)
        return response.json()
    
    def post_openai(self, prompt:str, context:str="You are a helpful assistant", model:str=OPENAI_MODEL):
        """
        Sends post request to the OpenAI completions server

        Args:
            prompt (str): The prompt to send to the model
            model (str): The name of the model to use

        Returns:
            response (str): Output from model given prompt
        """
        client = OpenAI(
        api_key=OPENAI_API_KEY
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

    def post_custom_endpoint(self, prompt:str, model:str=CUSTOM_MODEL, context:str="You are a helpful assistant", url=CUSTOM_ENDPOINT_URL):
        """
        Sends post request to the user inputted completions server

        Args:
            prompt (str): The prompt to send to the model
            model (str): The name of the model to use

        Returns:
            response (str): Output from model given prompt
        """

        headers = {
            "Authorization": f"Bearer {CUSTOM_API_KEY}",
            "Content-Type": "application/json"
        }

        json={
            "model": model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(url, headers=headers, json=json)
        return response.json(), headers | json

    def validate_output(self, response:dict):
        """
        Determines whether or not a JSON is a valid Internyl schema
        
        Args:
            response (dict): The outputted dictionary from the model or any dictionary
        
        Returns:
            value (str): Outputs an empty string if the dictionary is a valid Internyl schema 
            or a concatenated string of errors detailing the invalid parts of the response
        """
        if response == {'unrelated_website': True}:
            pass

        error = ''

        output_keys = list(response.keys())
        output_key = output_keys[0]

        if len(output_keys) > 1:
            error += f'ERROR: multiple categories detected; {len(output_keys)} categories: {output_keys}\n'
            error += f'Moving on to first category: {output_key}\n'

        categories = list(self.response.keys())
        if output_key not in categories:
            return f'ERROR: invalid schema response; {output_key} is an invalid category\n'
        
        output_sections = list(response[output_key].keys())
        schema_sections = list(self.response[output_key].keys())

        # Get all sections in the response that are not in the schema (invalid sections)
        invalid_sections = list(set(output_sections) - set(schema_sections))
        
        if invalid_sections:
            if len(invalid_sections) > 1:
                error += f'ERROR: invalid schema response; {invalid_sections} are invalid sections\n'
            else:
                error += f'ERROR: invalid schema response; {invalid_sections} is an invalid section\n'

        # Get all sections in the schema that are not in the response (missing sections)
        missing_sections = list(set(schema_sections) - set(output_sections))

        if missing_sections:
            if len(invalid_sections) > 1:
                error += f'ERROR: invalid schema response; {missing_sections} are missing\n'
            else:
                error += f'ERROR: invalid schema response; {missing_sections} is missing\n'
        
        return error + str(response)

    def parse_output(self, response):
        """
        Takes the response from the model and extracts the JSON output and parses it.
        Args:
            response (str): The response from the model

        Returns:
            value (dict or None): The dictionary response from the model assuming it returned a dictionary 
            or None if the response isn't a dictionary or if the response is {"unrelated_website": True}
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
        
        return parsed_response

    def handle_output(self, required_info, response):

        # Update for non bulk_process requirements
        if not required_info == "all":
            self.response[required_info].update(response[required_info])

            return response
        
        # Update for bulk process requirements
        for category in self.response:
            for section in self.response[category]:
                # The parsed response doesn't contain the categories like "overview"
                # so we have to loop through each section in the schema and update it
                # with the corresponding section in the parsed response
                try:
                    self.response[category][section] = response[section]
                except Exception: continue

                return response