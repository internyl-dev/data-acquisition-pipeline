
import asyncio
from bs4 import BeautifulSoup
from pprint import pp
from typing import Optional

from .models import History, FIFO, FILO, Queue, RootSchema, QueueItem, Fields

from .features.web_scrapers import PlaywrightClient
from .features.html_cleaners import HTMLDeclutterer, HTMLWhitespaceCleaner
from .features.schema_validators import SchemaValidationEngine
from .features.content_summarizers import ContentTrimmer, EmailExtractor, PhoneNumberExtractor, DateExtractor
from .features.ai_processors.prompt_chain import PromptChainExecutor
from .features.web_crawler import URLExtractor, URLProcessor, URLRanker, URLFilter
from .features.logger import Logger

from .utils import minimize_required_info, AIQueueFilter

class Main:
    def __init__(
        self,
        log_mode: bool = True,
        headless: bool = True,
        history: Optional[History] = None,
        queue: Optional[Queue] = None,
        schema: Optional[RootSchema] = None,
        log: Optional[Logger] = None,
        scraper: Optional[PlaywrightClient] = None,
        declutterer: Optional[HTMLDeclutterer] = None,
        whitespace_cleaner: Optional[HTMLWhitespaceCleaner] = None,
        validator: Optional[SchemaValidationEngine] = None,
        trimmer: Optional[ContentTrimmer] = None,
        email_extractor: Optional[EmailExtractor] = None,
        pn_extractor: Optional[PhoneNumberExtractor] = None,
        date_extractor: Optional[DateExtractor] = None,
        url_extractor: Optional[URLExtractor] = None,
        url_processor: Optional[URLProcessor] = None,
        url_ranker: Optional[URLRanker] = None,
        url_filter: Optional[URLFilter] = None,
        ai_queue_filter: Optional[AIQueueFilter] = None
        ) -> None:
        self.log_mode = log_mode
        self.headless = headless

        self.history = history or History()
        self.queue = queue or Queue()
        self.schema = schema or RootSchema()

        self.log = log or Logger(log_mode=self.log_mode)
        self.log.create_logging_files()
        self.log.apply_conditional_logging()

        self.scraper = scraper or PlaywrightClient()
        self.declutterer = declutterer or HTMLDeclutterer(remove_header=False, remove_nav=False)
        self.whitespace_cleaner = whitespace_cleaner or HTMLWhitespaceCleaner()
        self.validator = validator or SchemaValidationEngine()
        self.trimmer = trimmer or ContentTrimmer()
        self.email_extractor = email_extractor or EmailExtractor()
        self.pn_extractor = pn_extractor or PhoneNumberExtractor()
        self.date_extractor = date_extractor or DateExtractor()
        self.url_extractor = url_extractor or URLExtractor()
        self.url_processor = url_processor or URLProcessor()
        self.url_ranker = url_ranker or URLRanker()
        self.url_filter = url_filter or URLFilter()
        self.ai_queue_filter = ai_queue_filter or AIQueueFilter(self.log)

    def scrape(self, url) -> str:
        self.log.update("TRIMMER: Scraping...")
        try:
            raw_html: str = asyncio.run(self.scraper.scrape_url(url))
        except Exception as e:
            print(e)
            raise e

        return raw_html
    
    def add_to_queue(self, queue_item, all_target_info, raw_soup):
        new_urls = self.url_extractor.extract(raw_soup)

        for target_info in all_target_info:
            filtered_urls = self.url_filter.filter(new_urls, target_info)
            self.log.update(f"Filtering for {target_info}:", filtered_urls)
            for filtered_url in filtered_urls.values():
                filtered_url: str | None = self.url_processor.process_url(queue_item.url, filtered_url)
                if not filtered_url:
                    continue
                new_queue_item = QueueItem(filtered_url, target_fields=[target_info])

                # Skip links we've already visited
                if self.history.is_in(new_queue_item.url):
                    continue

                # If link is in queue, add info if it was not already there
                elif self.queue.is_in(new_queue_item):
                    q_item: QueueItem | None = self.queue.find(new_queue_item)
                    if q_item and target_info not in q_item.target_fields:
                        q_item.target_fields.append(target_info)

                else:
                    self.queue.add(new_queue_item)

    def run(self, url:str):
        target_info: list[Fields] | list[str] = self.validator.validate_all(self.schema)
        queue_item = QueueItem(url, target_info)
        self.base_url = url

        self.r(queue_item)

        self.schema.overview.link = self.base_url
        self.schema.overview.favicon = asyncio.run(self.scraper.scrape_favicon(url))

    def r(self, queue_item:QueueItem, depth:int=3):

        url: str = queue_item.url
        all_target_info: list[Fields] | list[str] = queue_item.target_fields

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
        
        raw_html: str = self.scrape(url)
        raw_soup = BeautifulSoup(raw_html, "html.parser")
        soup: BeautifulSoup = self.declutterer.clean(raw_soup)
        soup: BeautifulSoup = self.whitespace_cleaner.clean(soup)
        contents: str = soup.get_text()
        self.log.update(contents)

        response: RootSchema = PromptChainExecutor(schema=self.schema, all_target_info=all_target_info, log=self.log).run(contents)
        self.log.update(response)
        assert isinstance(response, RootSchema) # REMOVE LATER WHEN TYPE CHECKING IS FIXED
        self.schema = response

        all_target_info = self.validator.validate_all(self.schema)
        self.log.update(f"VALIDATOR: STILL NEED THE FOLLOWING INFO: {all_target_info}")
        self.add_to_queue(queue_item, all_target_info, raw_soup)

        if self.queue.get_length() > 5:
            self.log.update("EXCESSIVE QUEUE LENGTH DETECTED: PROMPTING AI QUEUE FILTER")
            new_queue_model = self.ai_queue_filter.add_queue(self.queue).invoke()
            new_queue = new_queue_model.new_queue
            self.log.update(new_queue)
            self.queue.keep_urls(new_queue)
            self.log.update(self.queue.items)

        while True:
            self.log.update(self.queue.peek())
            next_queue_item = self.queue.get()
            if not next_queue_item:
                break
            self.r(next_queue_item, depth=depth-1)
        
        return