
import asyncio
from bs4 import BeautifulSoup

import json
import datetime
from pprint import pformat
import atexit

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

        LOG_FILE_PATH = "logs/"
        if self.log_mode:
            time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.log_file = open(f"{LOG_FILE_PATH}{time_now}.txt", "a", encoding="utf-8")
            # Register log file closure on exit
            log_file = self.log_file
            atexit.register(lambda: log_file and log_file.close())


    def log(self, message, use_pformat=True):
        if self.log_mode:
            if use_pformat:
                message = pformat(message, width=160)
            print(message + '\n')

            # Remove parentheses and quotations to make log file look clean
            if isinstance(message, (list, tuple)):
                message = '\n'.join(str(m) for m in message)

            self.log_file.write(f'{message}\n\n')
            self.log_file.flush()

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

    def url_in_history(self, url):
        if url in self.history:

            # URL already processed: remove from queue to avoid duplicate extraction
            removed_item = self.queue.pop(url)

            self.log(f"'{removed_item}' already in history, removing from queue...")
            return True
        
    def max_depth_reached(self, depth):
        if depth <= 0:

            self.log(f"Maximum depth recursion reached ({depth}), ending recursion...")
            return True
        
    def recieved_all_required_info(self):
        if not self.get_required_info(self.response):
            
            # All information already recieved, return to avoid unecessary extraction

            self.log(f"All required info recieved: ending recursion...")
            return True

    def minimize_required_info(self, url, max_queue_length):
        if len(self.queue) > max_queue_length:

            # If the queue length is already really long, don't extract information that isn't needed
            # even if the information is specified as needed in the queue
            required_info = list(set(self.queue[url]) & set(self.get_required_info(self.response))) # Common required info between the two

            self.log(f"High queue length ({max_queue_length}): minimizing information from {self.queue[url]} to {required_info}...\n")
            self.queue[url] = required_info

    def guard_clauses(self, url, depth):
        if self.url_in_history(url):
            return True

        if self.max_depth_reached(depth):
            return True
    
        if self.recieved_all_required_info():
            return True



    def run(self, url:str, depth:int=2, bulk_process = True):

        self.log(f"Depth: {depth}. Beginning to scrape '{url}'...")
        self.queue.pop(url, None) # Remove from queue

        # GUARD CLAUSES
        if self.guard_clauses(url, depth):
            return

        # New URL: add to history for tracking
        self.history.append(url)

        # WEB SCRAPING
        html_contents = asyncio.run(self.scrape_html(url))

        # CONTENT SUMMARIZATION
        contents = self.summarize_contents(html_contents)

        # Find all required info and update object variable self.all_required_info
        if url in self.queue: # Avoid key error
            self.minimize_required_info(url, max_queue_length=1) # Minimizes the required info within the queue value
            self.all_required_info = self.queue[url]
        else:
            self.all_required_info = self.get_required_info(self.response)

        self.log(f"Extracting for the following info: {self.all_required_info}...")
        
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
                    self.log(self.queue)
                    self.log(self.response)
                    return
                
                if bulk_process:
                    break

        else:

            # Data collection mode off:
            # L> Just sends request to model

            for required_info in self.all_required_info:

                if bulk_process:
                    self.log("Overriding previous statement, instead performing bulk extraction...")
                    required_info = "all"
                    self.response['overview'].update({'link': url})

                prompt = self.create_prompt(contents, required_info)
                
                # Send AI a POST request asking to fill out schema chunks and update full schema
                self.log("Sending request...")
                response, request = self.post_custom_endpoint(prompt=prompt, context=self.prompts[required_info])
                self.log(request)

                self.log('Recieved response!')
                self.log(response)

                # parse_output returns None if the output from the model can't be parsed as a dictionary
                # or the output is {"unrelated_website": True}
                if not (parsed_data := self.parse_output(response)):
                    self.log("Either the output couldn't be parsed or the output indicated an unrelated website, ending recursion...")
                    return
                else:
                    if bulk_process: self.response = parsed_data
                    else: self.response.update(parsed_data)
                
                if bulk_process:
                    break
        
        self.log(json.dumps(self.response, indent=1))
        
        self.all_required_info = self.get_required_info(self.response)
        self.log(f'The following info is still required: {self.all_required_info}')
        all_links = self.get_all_links(BeautifulSoup(html_contents, features='html.parser'))
        self.log(f'All links:\n{json.dumps(all_links)}', use_pformat=False)

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

        self.log(f"Updated queue:\n{json.dumps(self.queue, indent=1)}")

        while self.queue:
            self.run(depth=depth-1, url=list(self.queue.keys())[0], bulk_process=False)
        
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
