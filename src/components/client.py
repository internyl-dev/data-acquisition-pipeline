
import json
from ast import literal_eval
import requests
from openai import OpenAI
from src.components.lib.prompts import prompts

from src.components.lib.logger import logger, api_log

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

        self.total_completions_tokens = 0
        self.total_prompt_tokens = 0
        self.total_reasoning_tokens = 0
        self.total_requests = 0

    def create_prompt(self, contents:str, required_info:str):
        """
        Creates the context for the language model to extract necessary info from.

        Args:
            contents (str): Contains the contents of the webpage
            required_info (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)
        
        Returns:
            value (str): The full prompt to be sent to the model
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
            f'ADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA: {schema}\n'
            f'TARGET PROGRAM INFORMATION:\n'
            f'Title: {self.response['overview']['title']}\n'
            f'Provider: {self.response['overview']['provider']}\n'
            f'Description: {self.response['overview']['description']}\n'
            f'WEBPAGE CONTENTS START HERE: {contents}'
            )

    def post_custom_endpoint(self, prompt:str, model:str=CUSTOM_MODEL, context:str="You are a helpful assistant", 
                             url=CUSTOM_ENDPOINT_URL, log_mode:bool=False):
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

        body={
            "model": model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": 0.0
        }

        if log_mode: 
            api_log.write(json.dumps(headers | body, indent=1) + '\n\n')
            api_log.flush()

        response = requests.post(url, headers=headers, json=body)
        response_json = response.json()

        completion_tokens = response_json["usage"]["completion_tokens"]
        prompt_tokens = response_json["usage"]["prompt_tokens"]
        reasoning_tokens = response_json["usage"]["completion_tokens_details"]["reasoning_tokens"]
        
        self.total_completions_tokens += completion_tokens
        self.total_prompt_tokens += prompt_tokens
        self.total_reasoning_tokens += reasoning_tokens
        self.total_requests += 1
        total_tokens = self.total_prompt_tokens + self.total_completions_tokens + self.total_reasoning_tokens

        if log_mode: 
            logger.info(f"Prompt tokens: {prompt_tokens} 
                        | Total prompt tokens: {self.total_prompt_tokens}")
            logger.info(f"Completion tokens: {completion_tokens} 
                        | Total completion tokens: {self.total_completions_tokens}")
            logger.info(f"Reasoning tokens: {reasoning_tokens} 
                        | Total reasoning tokens: {self.total_reasoning_tokens}")
            logger.info(f"Total tokens in this request: {prompt_tokens + completion_tokens + reasoning_tokens} 
                        | Total tokens: {total_tokens}")
            
            api_log.write(json.dumps(response_json, indent=1) + '\n\n')
            api_log.flush()

        return response_json

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
            logger.info(
                f"Successfully parsed data:\n"
                f"{json.dumps(parsed_response, indent=2)}"
                )

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            logger.error(f"Problematic JSON string:\n{json_string}")
            logger.warning(f"Using ast.literal_eval as fallback for non-JSON syntax...")
            try:
                # Try fixing invalid JSON that looks like a Python dict
                parsed_response = literal_eval(json_string)
            except Exception as eval_error:
                logger.error(f"ast.literal_eval failed to decode non-JSON syntax: {eval_error}")
                return None
            
        except KeyError as e:
            logger.error(f"Key error when accessing response: {e}. Check the structure of the response.")
            return None
        
        return parsed_response