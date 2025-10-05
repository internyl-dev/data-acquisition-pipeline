
import asyncio
from bs4 import BeautifulSoup
from pprint import pp
from dataclasses import dataclass

from .models import History, FIFO, FILO, Queue, RootSchema, QueueItem

from .features.web_scrapers import PlaywrightClient
from .features.html_cleaners import HTMLDeclutterer, HTMLWhitespaceCleaner
from .features.schema_validators import SchemaValidationEngine
from .features.content_summarizers import ContentTrimmer, EmailExtractor, PhoneNumberExtractor, DateExtractor
from .features.ai_processors.prompt_chain import PromptChainExecutor
from .features.web_crawler import URLExtractor, URLProcessor, URLRanker, URLFilter
from .features.logger import Logger

from .utils import minimize_required_info

@dataclass
class Main:
    log_mode: bool=True
    headless: bool=True

    history=None
    queue=None
    schema=None

    scraper=None
    declutterer=None
    whitespace_cleaner=None
    validator=None
    trimmer=None
    email_extractor=None
    pn_extractor=None
    date_extractor=None
    url_extractor=None
    url_processor=None
    url_ranker=None
    url_filter=None

    def __post_init__(self):

        self.history = self.history or History()
        self.queue = self.queue or Queue()
        self.schema = self.schema or RootSchema()

        self.scraper            = self.scraper            or PlaywrightClient()
        self.declutterer        = self.declutterer        or HTMLDeclutterer()
        self.whitespace_cleaner = self.whitespace_cleaner or HTMLWhitespaceCleaner()
        self.validator          = self.validator          or SchemaValidationEngine()
        self.trimmer            = self.trimmer            or ContentTrimmer()
        self.email_extractor    = self.email_extractor    or EmailExtractor()
        self.pn_extractor       = self.pn_extractor       or PhoneNumberExtractor()
        self.date_extractor     = self.date_extractor     or DateExtractor()
        self.url_extractor      = self.url_extractor      or URLExtractor()
        self.url_processor      = self.url_processor      or URLProcessor()
        self.url_ranker         = self.url_ranker         or URLRanker()
        self.url_filter         = self.url_filter         or URLFilter()

        self.log = Logger(log_mode=self.log_mode)
        self.log.create_logging_files()
        self.log.apply_conditional_logging()

    def scrape(self, url):
        self.log.update("TRIMMER: Scraping...")
        try:
            raw_html = asyncio.run(self.scraper.scrape_url(url))
        except Exception as e:
            print(e)
            raise e

        return raw_html
    
    def add_to_queue(self, queue_item, all_target_info, raw_soup):
        new_urls = self.url_extractor.extract(raw_soup)

        for target_info in all_target_info:
            filtered_urls = self.url_filter.filter(new_urls, target_info)
            for filtered_url in filtered_urls.values():
                filtered_url = self.url_processor.process_url(queue_item.url, filtered_url)
                new_queue_item = QueueItem(filtered_url, target_fields=[target_info])

                # Skip links we've already visited
                if self.history.is_in(new_queue_item.url):
                    continue

                # If link is in queue, add info if it was not already there
                elif self.queue.is_in(new_queue_item):
                    q_item = self.queue.find(queue_item)
                    if q_item and target_info not in q_item.target_fields:
                        q_item.target_fields.append(target_info)
                        self.queue.replace(q_item)

                else:
                    self.queue.add(new_queue_item)

    def run(self, url:str):
        target_info = self.validator.validate_all(self.schema)
        queue_item = QueueItem(url, target_info)
        self.base_url = url

        self.r(queue_item)

        self.schema.overview.link = self.base_url
        self.schema.overview.favicon = asyncio.run(self.scraper.scrape_favicon(url))

    def r(self, queue_item:QueueItem, depth:int=3):

        url = queue_item.url
        all_target_info = queue_item.target_fields

        # Guards
        if self.history.is_in(url):
            self.log.update(f"{queue_item.url} already in queue, returning...")
            return
        
        self.history.add(url)

        if depth <= 0:
            self.log.update(f"Max depth reached, returning...")
            return
        
        if self.queue.get_length() > 3:
            self.log.update("Excessively large queue length detected. " \
                            "Attempting to minimize target info...")
            self.log.update(queue_item.target_fields)
            minimize_required_info(queue_item, self.validator.validate_all(self.schema))
            self.log.update(queue_item.target_fields)

        if not all_target_info:
            self.log.update("No target info needed, returning...")
            return
        
        raw_html = self.scrape(url)
        raw_soup = BeautifulSoup(raw_html, "html.parser")
        soup = self.declutterer.clean(raw_soup)
        contents = self.whitespace_cleaner.clean(soup)

        response = PromptChainExecutor(schema=self.schema, all_target_info=all_target_info, log=self.log).run(contents)
        self.log.update(response)
        self.schema = response

        all_target_info = self.validator.validate_all(self.schema)
        self.log.update(f"VALIDATOR: STILL NEED THE FOLLOWING INFO: {all_target_info}")
        self.add_to_queue(queue_item, all_target_info, raw_soup)

        while True:
            self.log.update(self.queue.peek())
            next_queue_item = self.queue.get()
            if not next_queue_item:
                break
            self.r(next_queue_item, depth=depth-1)
        
        return