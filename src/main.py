
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
from .features.web_crawler import URLExtractor, URLProcessor, URLRanker, URLFilter, minimize_required_info
from .features.logger import Logger

from .utils import Guards

@dataclass
class Main(Guards):
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
        
        Guards.__init__(self)

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
        self.log.apply_conditional_logging()

    def scrape(self, url):
        self.log.update("Scraping...")
        try:
            raw_html = asyncio.run(self.scraper.scrape_url(url))
        except Exception as e:
            print(e)
            raise e

        return raw_html
    
    def add_to_queue(self, queue_item, all_target_info, raw_soup):
        new_urls = self.url_extractor.extract(raw_soup)

        for target_info in all_target_info:
            filtered_urls = self.url_filter.filter()
    
    def queue_new_links(self, base_url, raw_soup):

        if base_url in self.queue:
            minimize_required_info(base_url, 1)
            self.all_target_info = self.queue[base_url]
        else:
            self.all_target_info = SchemaValidationEngine().validate_all(self.schema)
        self.log.update(self.all_target_info)

        new_urls = self.url_extractor.extract(raw_soup)
        
        for required_info in self.all_target_info:
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

    def run(self, url:str):
        target_info = self.validator.validate_all(self.schema)
        queue_item = QueueItem(url, target_info)
        self.base_url = url
        self.schema.overview.link = self.base_url
        self.schema.overview.favicon = self.scraper.scrape_favicon()

        self.r(queue_item)

    def r(self, queue_item:QueueItem, depth:int=3):

        url = queue_item.url
        all_target_info = queue_item.target_fields

        # Guards
        if self.history.is_in(url):
            return
        
        self.history.add(url)

        if not self.validator.validate_all:
            return
        if depth <= 0:
            return
        
        raw_html = self.scrape(url)
        raw_soup = BeautifulSoup(raw_html, "html.parser")
        soup = self.declutterer.clean(raw_soup)
        contents = self.whitespace_cleaner.clean(soup)

        response = PromptChainExecutor(self.schema, all_target_info).run(contents)



    def run_loop(self, url:str, depth:int=2):

        if any([
            self.url_in_history(url),
            self.max_depth_reached(depth),
            self.received_all_target_info()
        ]):
            self.history.append(url)
            self.queue.pop(url, None)
            return
        
        self.history.append(url)
        self.queue.pop(url, None)

        raw_html = self.scrape(url)
        raw_soup = BeautifulSoup(raw_html, "html.parser")
        raw_soup = self.declutterer.clean(raw_soup)
        contents = self.whitespace_cleaner.clean(raw_soup)

        if url in self.queue:
            minimize_required_info(url, 1)
            self.all_target_info = self.queue[url]
        else:
            self.all_target_info = SchemaValidationEngine(self.schema).validate_all()

        self.ai_process_url(contents)
        
        self.queue_new_links(url, raw_soup)
        self.log.update(self.queue)

        while self.queue:
            self.run_loop(depth=depth-1, url=list(self.queue.keys())[0])

        return