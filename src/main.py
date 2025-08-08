
import asyncio
from bs4 import BeautifulSoup

import json
import atexit

from src.lib.config import Config

class Main(Config):
    def __init__(self, log_mode:bool=False, headless:bool=True):
        Config.__init__(self, log_mode, headless)

        self.history = []
        self.queue = {}

        self.all_required_info = []
        
        self.setup_logging_main()

        if self.log_mode:
            # Register log file closure on exit
            atexit.register(lambda: self.api_log and self.api_log.close())
        

    @staticmethod
    def get_required_info(json):
        required_info = []

        overview = json['overview']
        if overview['title'] == 'not provided':
            required_info.append('overview')

        eligibility = json['eligibility']
        if 'not provided' in eligibility['eligibility']['grades'] and list(eligibility['eligibility']['age'].values()) == ['not provided', 'not provided']:
            required_info.append('eligibility')

        dates = json['dates']
        if (
            any([deadline['date'] == 'not provided' and deadline['rolling_basis'] != True for deadline in dates['deadlines']]) or
            not any([deadline['priority'] == 'high' for deadline in dates['deadlines']])
            ):
            required_info.append('dates')

        locations = json['locations']
        if any([site['virtual'] == 'not provided' for site in locations['locations']]):
            required_info.append('locations')
        
        costs = json['costs']
        if any([plan['free'] == 'not provided' for plan in costs['costs']]):
            required_info.append('costs')

        contact = json['contact']
        if list(contact['contact'].values()) == ['not provided', 'not provided']:
            required_info.append('contact')

        return required_info

    def minimize_required_info(self, url, max_queue_length):
        if len(self.queue) > max_queue_length:

            # If the queue length is already really long, don't extract information that isn't needed
            # even if the information is specified as needed in the queue
            required_info = list(set(self.queue[url]) & set(self.get_required_info(self.response))) # Common required info between the two

            self.logger.info(f"High queue length ({max_queue_length}): minimizing information from {self.queue[url]} to {required_info}...\n")
            self.queue[url] = required_info

    def run(self, url:str, depth:int=2, bulk_process = True):

        self.logger.debug(f"Depth: {depth}")
        self.logger.info(f"Beginning to scrape '{url}'...")

        self.queue.pop(url, None)

        # GUARD CLAUSES
        if self.guard_clauses(url, self.history, self.queue, depth, self.get_required_info, self.response):
            return

        # New URL: add to history for tracking and remove from queue
        self.history.append(url)

        # WEB SCRAPING
        html_contents = asyncio.run(self.scrape_html(url))

        # HTML PARSING
        contents = self.parse_html(html_contents)



        # Find all required info and update object variable self.all_required_info
        if url in self.queue: # Avoid key error
            self.minimize_required_info(url, max_queue_length=1) # Minimizes the required info within the queue value
            self.all_required_info = self.queue[url]
        else:
            self.all_required_info = self.get_required_info(self.response)

        self.logger.debug(f"Extracting for the following info: {self.all_required_info}...")



        # CLIENT
        for required_info in self.all_required_info:

            if bulk_process:
                self.logger.debug("Overriding previous statement, instead performing bulk extraction...")
                required_info = "all"
                self.response['overview'].update({'link': url})

            # CONTENT SUMMARIZATION
            contents = self.truncate_contents(contents, required_info)

            prompt = self.create_prompt(contents, required_info)
            
            # Send AI a POST request asking to fill out schema chunks and update full schema
            self.logger.info("Sending request...")
            response = self.post_custom_endpoint(prompt=prompt, context=self.prompts[required_info], log_mode=self.log_mode)

            self.logger.info('Recieved response!')

            parsed_data = self.parse_output(response)

            if ("unrelated_website" in parsed_data):
                self.logger.warning(f"Unrelated website detected (URL: {url}), ending recursion...")
                return
            
            # parse_output returns None if the output from the model can't be parsed as a dictionary
            if (not parsed_data):
                return
            
            # Update the response based on the method of extraction
            if bulk_process: 
                self.response = parsed_data
                break
                # End loop
 
            self.response.update(parsed_data)
            # Continue loop
        

        
        self.all_required_info = self.get_required_info(self.response)
        self.logger.debug(f'The following info is still required: {self.all_required_info}')
        
        all_links = self.get_all_links(BeautifulSoup(html_contents, features='html.parser'))
        self.logger.debug(f'All links:\n{json.dumps(all_links)}')



        for required_info in self.all_required_info:
            filtered_links = self.filter_links(all_links, required_info)

            for link in filtered_links.values():
                link = self.process_link(url, link)

                # Skip links we've already visited
                if link in self.history:
                    continue

                # If link is in queue: add info if it was not already there
                elif link in self.queue:
                    if required_info not in self.queue[link]:
                        self.queue[link].append(required_info)

                # Link is not in history or queue: add it into the queue
                else:
                    self.queue[link] = [required_info]



        self.logger.debug(f"Updated queue:\n{json.dumps(self.queue, indent=1)}")

        while self.queue:
            self.run(depth=depth-1, url=list(self.queue.keys())[0], bulk_process=False)
        
        return