
import asyncio

import json
import atexit

from .utils.base import Base

class Main(Base):
    def __init__(self, log_mode:bool=False, headless:bool=True):
        Base.__init__(self, log_mode, headless)

        self.history = []
        self.queue = {}
        
        self.setup_logging_main()

        if self.log_mode:
            # Register log file closure on exit
            atexit.register(lambda: self.api_log and self.api_log.close())

    def run(self, url:str, depth:int=2, bulk_process:bool=True, first_run=True):
        
        if first_run:
            self.url = url
            first_run = False

        self.logger.debug(f"Depth: {depth}")
        self.logger.info(f"Beginning to scrape '{url}'...")

        # GUARD CLAUSES
        # 1. Checks if URL is in history
        # 2. Checks if max depth has been reached
        # 3. Checks if all required info has already been collected
        if self.guard_clauses_main(url, depth):
            self.history.append(url)
            self.queue.pop(url, None)
            return

        # New URL: add to history for tracking and remove from queue
        self.history.append(url)
        self.queue.pop(url, None)

        # WEB SCRAPING
        # Using Playwright, we scrape the HTML contents from a url and get the inner text
        try:
            raw_html = asyncio.run(self.scrape_html(url))
        except Exception as e:
            self.logger.error(e)
            return

        # HTML PARSING
        # 1. Remove unecessary bloating HTML elements from the raw html
        # 2. Remove any unecessary whitespace
        contents = self.parse_html(raw_html)

        # Find all required info and update object variable self.all_required_info
        if url in self.queue: # Avoid key error
            self.minimize_required_info(url, max_queue_length=1) # Minimizes the required info within the queue value
            self.all_required_info = self.queue[url]
        else:
            self.all_required_info = self.get_required_info()

        self.logger.debug(f"Extracting for the following info: {self.all_required_info}...")

        # MODEL CLIENT
        # 1. Iterates through the required info,
        # 2. Summarizes the HTML contents through each iteration based off of keywords,
        # 3. Makes prompts based on collecting the required info,
        # 4. Sends a request to the model,
        # 5. Updates the response based on the response from the model
        self.model_client_main(url, contents, bulk_process)
        
        # Check for required info after the new information has been added
        self.all_required_info = self.get_required_info()
        self.logger.debug(f'The following info is still required: {self.all_required_info}')

        # WEB CRAWLING
        # 1. Filter links based on keywords in the content or the URL
        # 2. Check if link is in history, continue iterating without changing the queue if it is
        # 3. Check if link is already in queue, add information if it is
        # 4. Else add link and required info to queue
        self.web_crawling_main(raw_html, url)
        self.logger.debug(f"Updated queue:\n{json.dumps(self.queue, indent=1)}")

        while self.queue and depth > 1:
            self.run(depth=depth-1, url=list(self.queue.keys())[0], bulk_process=False)
        
        return