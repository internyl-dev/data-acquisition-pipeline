
from bs4 import BeautifulSoup

from .url_processor import URLProcessor

class URLExtractor:
    def __init__(self, processor:URLProcessor=None):
        self.processor = processor or URLProcessor()

    def _get_all_anchors(self, soup:BeautifulSoup):
        """
        Finds all anchor elements from within some HTML contents and returns their content and HREFs if they are valid links.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            href[url] (dict): The contents of anchor elements that have valid links as HREFs 
            with the keys as the content from the original anchor element
        """
        anchors = soup.find_all('a')
        return anchors

    def _filter_valid_urls(self, anchors:list):
        urls = {}

        for anchor in anchors:
            try:
                # Add link to dictionary with the associated text being the key
                # L> For future filtering based off of keywords
                url = anchor.get('href').strip()
                text = anchor.get_text().strip()
                
                if self.processor.is_url(url):
                    urls[text] = url

            except Exception: 
                continue

        return urls
    
    def extract(self, soup:BeautifulSoup):
        anchors = self._get_all_anchors(soup)
        return self._filter_valid_urls(anchors)