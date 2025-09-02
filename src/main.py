
import asyncio
import json
from bs4 import BeautifulSoup
import logging

from .features.web_scrapers import PlaywrightClient
from .features.html_cleaners import HTMLDeclutterer, HTMLWhitespaceCleaner
from .features.schema_validators import SchemaValidationEngine
from .features.content_summarizers import ContentTrimmer, EmailExtractor, PhoneNumberExtractor, DateExtractor
from .features.ai_processors import azure_chat_openai, create_chat_prompt_template, PromptBuilder
from .features.web_crawler import URLExtractor, URLProcessor, URLRanker, URLFilter, minimize_required_info
from .features.logger import Logger, Observable

from .utils import Guards

class Main(Guards):
    def __init__(self, log_mode:bool=False, headless:bool=True, 
                 scraper=None, declutterer=None, whitespace_cleaner=None, 
                 trimmer=None, email_extractor=None, pn_extractor=None, date_extractor=None,
                 url_extractor=None, url_processor=None, url_ranker=None, url_filter=None):
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

        self.scraper            = scraper            or PlaywrightClient()
        self.declutterer        = declutterer        or HTMLDeclutterer()
        self.whitespace_cleaner = whitespace_cleaner or HTMLWhitespaceCleaner()
        self.trimmer            = trimmer            or ContentTrimmer()
        self.email_extractor    = email_extractor    or EmailExtractor()
        self.pn_extractor       = pn_extractor       or PhoneNumberExtractor()
        self.date_extractor     = date_extractor     or DateExtractor()
        self.url_extractor      = url_extractor      or URLExtractor()
        self.url_processor      = url_processor      or URLProcessor()
        self.url_ranker         =  url_ranker        or URLRanker()
        self.url_filter         = url_filter         or URLFilter()

        self.log = Logger(log_mode=True)
        self.log.apply_conditional_logging()

    def _scrape(self, url):
        self.log.update("Scraping...")
        try:
            raw_html = asyncio.run(self.scraper.scrape_url(url))
        except Exception as e:
            print(e)
            raise e

        return raw_html
    
    def __build_prompt(self, contents, required_info):
            
        builder = PromptBuilder()
        builder.add_schema_context(self.schema) \
                .add_title(self.schema["overview"]["title"]) \
                .add_description(self.schema["overview"]["description"]) \
                .add_provider(self.schema["overview"]["provider"]) \
                .add_webpage_contents(contents)
        instructions = builder.get_prompt_obj().get_prompt()

        chat_prompt_template = create_chat_prompt_template(required_info)
        prompt = chat_prompt_template.format_prompt(query=instructions)

        return prompt
    
    def _ai_process_url(self, contents):
        for required_info in self.all_required_info:

            if len(self.all_required_info) == 6:
                required_info = "all"
            
            trimmed_contents = self.trimmer.truncate_contents(contents, required_info, 500, 1)
            prompt = self.__build_prompt(trimmed_contents, required_info)

            self.log.update("Sending request...")
            response = azure_chat_openai.invoke(prompt)

            response_dict = json.loads(response.model_dump()["content"])
            self.log.update(response_dict)
            
            if len(self.all_required_info) == 6:
                self.schema = response_dict
                break
            else:
                self.schema[required_info] = response_dict
                continue
    
    def _queue_new_links(self, base_url, raw_soup):

        self.all_required_info = SchemaValidationEngine(self.schema).validate_all()

        new_urls = self.url_extractor.extract(raw_soup)
        
        for required_info in self.all_required_info:
            filtered_urls = self.url_filter.filter(new_urls, required_info)
            for filtered_url in filtered_urls.values():

                filtered_url = self.url_processor.process_url(base_url, filtered_url)

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

    def run(self, url:str, depth:int=2):
        
        if not hasattr(self, "url"):
            self.url = url

        if any([
            self.url_in_history(url),
            self.max_depth_reached(depth),
            self.received_all_required_info(SchemaValidationEngine(self.schema))
        ]):
            self.history.append(url)
            self.queue.pop(url, None)
            return
        
        self.history.append(url)
        self.queue.pop(url, None)

        raw_html = self._scrape(url)
        raw_soup = BeautifulSoup(raw_html, "html.parser")
        raw_soup = self.declutterer.clean(raw_soup)
        contents = self.whitespace_cleaner.clean(raw_soup)

        if url in self.queue:
            minimize_required_info(url, 1)
            self.all_required_info = self.queue[url]
        else:
            self.all_required_info = SchemaValidationEngine(self.schema).validate_all()

        self._ai_process_url(contents)
        
        self._queue_new_links(url, raw_soup)

        while self.queue:
            self.run(depth=depth-1, url=list(self.queue.keys())[0])

        return