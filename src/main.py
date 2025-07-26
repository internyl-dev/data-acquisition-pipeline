
import asyncio
from bs4 import BeautifulSoup
from pprint import pprint

# Import classes
from src.components.web_scraping import WebScraping
from src.components.html_parsing import HTMLParsing
from src.components.content_summ import ContentSummarization
from src.components.client import Client
from src.components.web_crawling import WebCrawling

import time
def stopwatch(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f'{func.__name__}:', round(time.time() - start, 2), 'seconds')
        return result
    return wrapper

class Main(WebScraping, HTMLParsing, ContentSummarization, Client, WebCrawling):
    def __init__(self, log_mode:bool=False, collect_data:bool=False, headless:bool=True):
        WebScraping.__init__(self, headless=headless)
        HTMLParsing.__init__(self)
        ContentSummarization.__init__(self)
        Client.__init__(self)
        WebCrawling.__init__(self)

        self.history = []
        self.queue = {}

        self.all_required_info = []

        self.log_mode = log_mode
        self.collect_data = collect_data

    @staticmethod
    def get_required_info(json):
        required_info = []

        overview = json['overview']
        if overview['provider'] == 'not provided' or not overview['subject']:
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

    def url_is_in_history(self, url):
        if url in self.history:

            # URL already processed: remove from queue to avoid duplicate extraction
            removed_item = self.queue.pop(url)

            if self.log_mode:
                print(f"'{removed_item}' already in history, removing from queue...\n")

            return True
        
    def max_depth_reached(self, depth):
        if depth <= 0:

            if self.log_mode:
                print(f"Maximum depth recursion reached ({depth})\n")
                
            return True
        
    def recieved_all_required_info(self):
        if not (all_required_info := self.get_required_info(self.response)):
            
            # All information already recieved, return to avoid unecessary extraction

            if self.log_mode:
                print(f"All required info recieved: ending recursion...")

            return True
        else:
            self.all_required_info = all_required_info

    def minimize_required_info(self, url, max_queue_length):
        if len(self.queue) > max_queue_length:

            # If the queue length is already really long, don't extract information that isn't needed
            # even if the information is specified as needed in the queue
            required_info = list(set(self.queue[url]) & set(self.all_required_info))

            if self.log_mode:
                print(f"High queue length ({max_queue_length}): minimizing information from {self.queue[url]} to {required_info}...\n")

            self.queue[url] = required_info

    def guard_clauses(self, url, depth):
        if self.url_is_in_history(url):
            return True

        if self.max_depth_reached(depth):
            return True
    
        if self.recieved_all_required_info():
            return True


    def run(self, url:str, depth:int=2, bulk_process = True):

        if self.log_mode:
            print(f"Depth: {depth}. Beginning to scrape '{url}'...\n")

        if self.guard_clauses(url, depth):
            return

        # New URL: add to history for tracking
        self.history.append(url)

        self.minimize_required_info(url, 1)

        html_contents = asyncio.run(self.scrape_html(url))
        raw_soup = BeautifulSoup(html_contents, features='html.parser') # Save aside html_contents for get_all_links

        soup = BeautifulSoup(html_contents, features='html.parser')
        soup = self.declutter_html(soup)
        contents = self.clean_whitespace(soup)

        if url in self.queue: # Avoid key error
            self.all_required_info = self.queue[url]
            self.queue.pop(url)

        if self.log_mode:
            print(f"Extracting for the following info: {self.all_required_info}...\n")
        
        if self.collect_data:

            # Data collection mode:
            # L> Will append all scraped context to DATA_FILE_PATH
            # L> Up to user to input extracted information
            # L> Used for data collection for fine-tuning

            for required_info in self.all_required_info:

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

            for required_info in self.all_required_info:

                if bulk_process:
                    required_info = "all"

                pprint(prompt := self.create_prompt(contents, required_info))

                # Send AI a POST request asking to fill out schema chunks and update full schema
                print("Sending request...")
                pprint(response := self.post_openai(prompt=prompt, context=self.prompts[required_info]))

                # handle_output returns None if the output from the model can't be parsed as a dictionary
                # or the output is {"unrelated_website": True}
                if not (parsed_data := self.handle_output(response, required_info)):
                    return

                self.response.update({'link': url})

                if bulk_process:
                    break
        
        pprint(self.response)
        
        self.all_required_info = self.get_required_info(self.response)
        all_links = self.get_all_links(raw_soup)
        pprint(all_links)

        for required_info in self.all_required_info:
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



#Instance = Main(log_mode = True, collect_data=False)

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
#Instance.run('https://www.metmuseum.org/about-the-met/internships/high-school/summer-high-school-internships')
