
from lib.scrape_html import *
import asyncio
from bs4 import BeautifulSoup
import re
from lib.keywords import keywords
from lib.client import ask_llama
from lib.read_json import get_required_info
import json
from pprint import pprint

import time
def stopwatch(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f'{func.__name__}:', round(time.time() - start, 2), 'seconds')
        return result
    return wrapper

class Main:
    def __init__(self, log_mode:bool=False, collect_data:bool=False):

        SCHEMA_FILE_PATH = 'main/lib/schemas.json'
        self.DATA_FILE_PATH = 'main/scraped-html-json-responses.jsonl'

        with open(SCHEMA_FILE_PATH, 'r', encoding='utf-8') as file:
            self.response = json.load(file)
        
        self.data = {"messages": [{"role": "user","content": ""},{"role": "assistant","content": {}}]}

        from lib.prompts import prompts
        self.prompts = prompts

        self.history = []
        self.queue = {}

        self.log_mode = log_mode
        self.collect_data = collect_data

    @staticmethod
    def scrape_html(url:str):
        """
        Sends URL to Playwright to extract HTML contents.

        Args:
            url (str): URL to target website
        
        Returns:
            html_contents (str): The contents of the HTML of the target website
        """
        html_contents = asyncio.run(get_html(url))
        return html_contents

    @staticmethod
    def declutter_html(soup:BeautifulSoup):
        """
        Removes all HTML elements from BeautifulSoup object that would clutter the page contents.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            soup (BeautifulSoup): HTML contents with cluttering elements removed
        """

        # headers, navs, and footers typically contain links to other parts of the website
        # L> Excessively clutter context, especially when truncating for keywords
        for element in ['header', 'nav', 'footer']:
            elements = soup.find_all(element)  
            for elm in elements:
                elm.decompose()
        
        # These are all common form elements that can have text
        # Often contain tens of options that just clutter context
        for element in ['select', 'textarea', 'button', 'option']:
            elements = soup.find_all(element)
            for elm in elements:
                elm.decompose()
        
        return soup
    
    @staticmethod
    def clean_whitespace(soup:BeautifulSoup):
        """
        Converts a BeautifulSoup object to a string while also removing excessive white space from the string.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page
        
        Returns:
            contents (str): Webpage contents as a string without excessive white space.
        """

        # Remove excessive white space
        contents = soup.get_text().strip()
        contents = re.sub(r'\n\s*\n+', '\n', contents)
        contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE)

        return contents

    @staticmethod
    def truncate_contents(contents:str, required_info:str, word_limit:int=1500): # Using word count as a rough estimator for token count
        """
        Truncates any string separated by new lines 
        and returns only the lines near to and containing keywords based off of the info required.

        Args:
            contents (str): Contains the contents of the webpage
            info_required (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)
            word_limit (int, optional): Automatically set to 1500, the word limit for the string to start truncating

        Returns:
            value (str): Truncated contents of the webpage
        """

        # If the length of the contents is less than the word limit:
        # L> Return the full contents because the model can handle the relatively smaller word count
        # If the required info is overview:
        # L> Return the full contents if the required info is 'overview so that the model can make a general description
        if len(contents.split()) < word_limit or required_info == 'overview':
            return contents

        # Truncate for dates as well as keywords if required info is 'dates'
        if required_info == 'dates':
            keywrds = (keywords[required_info] 
                        + find_dates(contents))
        
        # Truncate for emails and phone numbers as well as keywords if required info is 'contact'
        elif required_info == 'contact':
            keywrds = (keywords[required_info] 
                        + find_emails(contents) 
                        + find_phone_numbers(contents))
            
        # Or simply truncate for keywords associated with the required info
        else:
            keywrds = keywords[required_info]

        return truncont(contents, keywrds, 1)

    def create_context(self, contents:BeautifulSoup|str, required_info:str):
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
            self.prompts[required_info] + '\n'
            + '\nADD NEWLY FOUND INFORMATION ONTO THIS SCHEMA: '
            + schema + '\n'
            + '\nTARGET INTERNSHIP INFORMATION: '
            + 'Title: ' + self.response['overview']['title'] + '\n'
            + 'Provider: ' + self.response['overview']['provider'] + '\n'
            + 'Description: ' + self.response['overview']['description'] + '\n'
            + '\nWEBPAGE CONTENTS START HERE: '
            + self.truncate_contents(contents, required_info)
            )

    @staticmethod
    def send_request(context:str):
        """
        Sends POST request with prompt attached to server that is hosting the model.

        Args:
            context (str): Prompt and content of webpage
        
        Returns:
            response (str): Response from model
        """
        response = ask_llama(context).json()
        return response

    @staticmethod
    def get_all_links(soup:BeautifulSoup):
        """
        Finds all anchor elements from within some HTML contents and returns their content and HREFs if they are valid links.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            new_links (dict): The contents of anchor elements that have valid links as HREFs 
            with the keys as the content from the original anchor element
        """
        new_links = {}
        links = soup.find_all('a')

        for link in links:
            url = link.get('href')
            text = link.get_text().strip()

            try:
                # Add link to dictionary with the associated text being the key
                # L> For future filtering based off of keywords
                if is_link(url):
                    new_links[text] = url

            except Exception: continue

        return new_links

    @staticmethod
    def filter_links(links:dict, required_info:str):
        """
        Filters all anchor elements based on their content and URL with keywords corresponding to the required info.

        Args:
            links (dict): The contents of anchor elements that have valid links as HREFs with the keys as the content from the original anchor element
            required_info (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)

        Returns:
            filtered_links (dict): Only the links that contain the relevant keywords in either their content or url
        """
        filtered_links = {}
        for content in links:
            for keyword in keywords['link'][required_info]:

                # If the keyword was found in the text or HREF, add it to the new dictionary
                if re.search(fr'{keyword}', content, re.I) or re.search(fr'{keyword}', links[content], re.I):
                    filtered_links[content] = links[content]
        
        return filtered_links
    
    @staticmethod
    def process_link(url:str, link:str):
        """
        Takes the contents of any HREF assuming that the HREF is an absolute or relative path to a webpage and turns it in an absolute link.

        Args:
            url (str): Absolute webpage URL from which any relative links will be joined with
            link (str): Absolute or relative URL

        Returns:
            value (str): Either the absolute URL result from joining a given absolute URL and relative URL or just the newly given absolute URL.
        """
        if link[0] == '/':
            return '/'.join(url.split('/')[0:3]) + link

        elif link[0:7] == 'http://' or link[0:8] == 'https://':
            return link

        elif link[-1] == '/':
            if not url[-1] == '/':
                url += '/'
            return url + link

    def read_last_jsonl(self):
        """
        Reads last line in a JSONL file using byte reading.

        Returns:
            value (dict): The parsed JSON content
        """
        with open(self.DATA_FILE_PATH, "rb") as f:
            f.seek(0, 2)  # Go to end of file
            pos = f.tell() - 1

            while pos > 0:
                f.seek(pos)
                char = f.read(1)
                if char == b"\n":
                    # Read the next line after newline
                    last_line = f.readline().decode("utf-8").strip()
                    if last_line != '':
                        return json.loads(last_line)
                pos -= 1

            # If we reach start of file, read from beginning (in case single line no newline)
            f.seek(0)
            last_line = f.readline().decode("utf-8").strip()
            return json.loads(last_line)

    def save_to_jsonl(self, context:str):
        """
        Dumps the prompt and context into the JSONL file 
        and waits until the user has inputted content in the form of the ideal model response.

        Args:
            context (str): The prompt and context to give to the model
        
        Returns:
            value (dict): The user-inputted ideal response
        """
        data = self.data.copy()
        data['messages'][0]['content'] = context

        with open(self.DATA_FILE_PATH, "a+", encoding="utf-8") as file:
            file.write(json.dumps(self.data) + "\n")
            file.flush()

            loops = 0

            c = self.read_last_jsonl()
            while not c['messages'][1]['content']:
                loops += 1
                time.sleep(1)
                c = self.read_last_jsonl()
                print('Read last line', loops, 'time(s)')
        
        return self.read_last_jsonl()['messages'][1]['content']
    
    def create_data(self, context:str, required_info:str):
        """
        Dumps the data JSON schema with context into JSONL file, waits for user input, and reads the response.

        Args:
            context (str): 

        Returns:
            value (bool): Returns True if the response is "{'unrelated_website': True}"
        """
        response = self.save_to_jsonl(context)
        
        if response == {'unrelated_website': True}:
            return True
            
        self.response[required_info].update(response[required_info])
    
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

    def run(self, url:str, depth:int=2, bulk_process = True):

        if self.log_mode:
            print(f"Depth: {depth}. Beginning to scrape '{url}'...\n")

        # GUARD CLAUSES

        if url in self.history:

            # URL already processed: remove from queue to avoid duplicate extraction
            removed_item = self.queue.pop(url)

            if self.log_mode:
                print(f"'{removed_item}' already in history, removing from queue...\n")

            return
            
        else:

            # New URL: add to history for tracking
            self.history.append(url)

        if depth <= 0:

            if self.log_mode:
                print(f"Maximum depth recursion reached ({depth})\n")
                
            return
        
        if not (all_required_info := get_required_info(self.response)):
            
            # All information already recieved, return to avoid unecessary extraction

            if self.log_mode:
                print(f"All required info recieved: ending recursion...")

            return

        if len(self.queue) > 2:

            # If the queue length is already really long, don't extract information that isn't needed
            # even if the information is specified as needed in the queue
            required_info = list(set(self.queue[url]) & set(all_required_info))

            if self.log_mode:
                print(f"High queue length: minimizing information from {self.queue[url]} to {required_info}...\n")

            self.queue[url] = required_info


        html_contents = self.scrape_html(url)
        raw_soup = BeautifulSoup(html_contents, features='html.parser') # Save aside html_contents for get_all_links

        soup = BeautifulSoup(html_contents, features='html.parser')
        soup = self.declutter_html(soup)
        contents = self.clean_whitespace(soup)

        if url in self.queue: # Avoid key error
            all_required_info = self.queue[url]
            self.queue.pop(url)

        if self.log_mode:
            print(f"Extracting for the following info: {all_required_info}...\n")
        
        if self.collect_data:

            # Data collection mode:
            # L> Will append all scraped context to DATA_FILE_PATH
            # L> Up to user to input extracted information
            # L> Used for data collection for fine-tuning

            for required_info in all_required_info:

                if bulk_process:
                    required_info = "all"
                    
                context = self.create_context(contents, required_info)

                if self.create_data(context, required_info):
                    # create_data returns True if the assistant content is "{'unrelated_website': True}"
                    # L> Means that the website that the content was extracted from
                    #    did not include information about the target internship
                    pprint(self.queue)
                    pprint(self.response)
                    return
                
                if bulk_process:
                    break

        else:     

            # Data collection mode off:
            # L> Just sends request to presumably fine-tuned model

            for required_info in all_required_info:

                if bulk_process:
                    required_info = "all"

                context = self.create_context(contents, required_info)

                # Send AI a POST request asking to fill out schema chunks and update full schema
                print("Sending request...")
                pprint(response := self.send_request(context))

                # handle_output returns None if the output from the model can't be parsed as a dictionary
                # or the output is {"unrelated_website": True}
                if not (parsed_data := self.handle_output(response, required_info)):
                    return

                self.response.update({'link': url})

                if bulk_process:
                    break
        
        pprint(self.response)
        
        all_required_info = get_required_info(self.response)
        all_links = self.get_all_links(raw_soup)
        pprint(all_links)

        for required_info in all_required_info:
            filtered_links = self.filter_links(all_links, required_info)

            for link in filtered_links.values():
                link = self.process_link(url, link)

                # Skip links we've already visited
                if link in self.history:
                    continue

                # Add info if it was not there already
                elif link in self.queue:
                    if required_info not in self.queue[link]:
                        self.queue[link].append(required_info)

                else:
                    self.queue[link] = [required_info]

        pprint(self.queue)

        while self.queue:
            self.run(list(self.queue.keys())[0], bulk_process=False)
        
        return



Instance = Main(log_mode = True, collect_data=False)

# Instructions to use in data collection mode:
# 1. Input the internship overview page link into the run method as an argument
# 2. A new JSONL file will open which will follow the DATA_URL_PATH
# 3. Open the file and copy the prompt
# 4. Put the prompt in a capable LLM
#    L> Ensure that the output is the correct schema and that the data is accurate
#    L> Convert the schema into one line if needed
# 5. Paste the one-line schema into the assisstant.contents section
# 6. A new prompt will appear, copy the prompt and repeat from step 4
# 7. If no new prompt appears, you are done, if you get an error, you did one of the steps wrong or pasted the schema in wrong
Instance.run('https://www.metmuseum.org/about-the-met/internships/high-school/summer-high-school-internships')
