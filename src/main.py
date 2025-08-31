
import asyncio
import json
from bs4 import BeautifulSoup

from .features.web_scrapers import PlaywrightClient
from .features.html_cleaners import HTMLDeclutterer, HTMLWhitespaceCleaner
from .features.schema_validators import SchemaValidationEngine
from .features.content_summarizers import ContentTrimmer, EmailExtractor, PhoneNumberExtractor, DateExtractor
from .features.ai_processors import azure_chat_openai, create_chat_prompt_template, PromptBuilder
from .features.web_crawler import URLExtractor, URLProcessor, URLRanker, URLFilter

from .utils import Guards

class Main(Guards):
    def __init__(self, log_mode:bool=False, headless:bool=True):
        Guards.__init__(self)

        self.history = []
        self.queue = {}
        
        try:
            with open(file="src/assets/schemas.json", mode="r", encoding="utf-8") as f:
                self.schema = json.load(f)
        except FileNotFoundError as e:
            print(e)
            raise e
        except json.JSONDecodeError as e:
            print(e)
            raise e
        
        self.scraper = PlaywrightClient()
        self.declutterer, self.whitespace_cleaner = HTMLDeclutterer(), HTMLWhitespaceCleaner()
        self.trimmer = ContentTrimmer()
        self.email_extractor, self.pn_extractor, self.date_extractor = EmailExtractor(), PhoneNumberExtractor(), DateExtractor()
        self.url_extractor = URLExtractor()
        self.url_processor = URLProcessor()
        self.url_ranker = URLRanker()
        self.url_filter = URLFilter()
        
    def minimize_required_info(self, url, max_queue_length):
        if len(self.queue) > max_queue_length:

            # If the queue length is already really long, don't extract information that isn't needed
            # even if the information is specified as needed in the queue
            required_info = list(set(self.queue[url]) & set(self.get_required_info(self.response))) # Common required info between the two

            self.logger.info(f"High queue length ({max_queue_length}): minimizing information from {self.queue[url]} to {required_info}...\n")
            self.queue[url] = required_info

    def run(self, url:str, depth:int=2, bulk_process:bool=True, first_run=True):
        
        if not hasattr(self, "url"):
            self.url = url

        if any([
            self.url_in_history(url),
            self.max_depth_reached(depth),
            self.received_all_required_info(SchemaValidationEngine(self.schema))
        ]): 
            return
        
        self.history.append(url)
        self.queue.pop(url, None)

        try:
            raw_html = asyncio.run(self.scraper.scrape_url(url))
        except Exception as e:
            print(e)
            return
        
        raw_soup = BeautifulSoup(raw_html, "html.parser")

        raw_soup = self.declutterer.clean(raw_soup)
        contents = self.whitespace_cleaner.clean(raw_soup)

        if url in self.queue:
            self.minimize_required_info(url, 1)
            self.all_required_info = self.queue[url]
        else:
            self.all_required_info = SchemaValidationEngine(self.schema).validate_all()

        for required_info in self.all_required_info:

            if bulk_process:
                required_info = "all"
            
            contents = self.trimmer.truncate_contents(contents, required_info, 500, 1)

            builder = PromptBuilder()
            builder.add_schema_context(self.schema) \
                   .add_title(self.schema["overview"]["title"]) \
                   .add_description(self.schema["overview"]["description"]) \
                   .add_provider(self.schema["overview"]["provider"]) \
                   .add_webpage_contents(contents)
            instructions = builder.get_prompt_obj().get_prompt()

            prompt = create_chat_prompt_template(instructions, required_info)
            response = azure_chat_openai.invoke(prompt)

            response_dict = response.model_dump()
            
            if bulk_process:
                self.schema = response_dict
                break
            else:
                self.schema[required_info] = response_dict
                continue
        
        self.all_required_info = SchemaValidationEngine(self.schema).validate_all()

        new_urls = self.url_extractor.extract(raw_soup)
        
        for required_info in self.all_required_info:
            filtered_urls = self.url_filter.filter(new_urls, required_info)
            for filtered_url in filtered_urls.values():

                filtered_url = self.url_processor.process_url(url, filtered_url)

                # Skip links we've already visited
                if filtered_url in self.history:
                    continue

                # If link is in queue: add info if it was not already there
                elif filtered_url in self.queue:
                    if required_info not in self.queue[filtered_url]:
                        self.queue[filtered_url].append(required_info)

                # Link is not in history or queue: add it into the queue
                else:
                    self.queue[filtered_url] = [required_info]

        while self.queue:
            self.run(depth=depth-1, url=list(self.queue.keys())[0], bulk_process=False)

        return