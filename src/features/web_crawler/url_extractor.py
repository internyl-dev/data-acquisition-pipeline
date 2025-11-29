
from bs4 import BeautifulSoup
from bs4.element import ResultSet, NavigableString, PageElement, Tag, AttributeValueList
from collections.abc import Sequence
from typing import Optional, NewType

from .url_processor import URLProcessor

AnchorText = NewType("AnchorText", str)
Href = NewType("Href", str)

class URLExtractor:
    def __init__(self, processor: Optional[URLProcessor] = None) -> None:
        self.processor = processor or URLProcessor()

    def _get_all_anchors(self, soup: BeautifulSoup) -> ResultSet[NavigableString | PageElement | Tag]:
        """
        Finds all anchor elements from within some HTML contents and returns their content and HREFs if they are valid links.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            urls (ResultSet[NavigableString | PageElement | Tag]): All of the anchor elements within the `BeautifulSoup` object
        """
        anchors: ResultSet[NavigableString | PageElement | Tag] = soup.find_all('a')
        return anchors

    def _filter_valid_urls(self, anchors: ResultSet[NavigableString | PageElement | Tag]) -> dict[AnchorText, Href]:
        urls: dict[AnchorText, Href] = {}

        for anchor in anchors:
            if not isinstance(anchor, Tag):
                continue
            try:
                # Add link to dictionary with the associated text being the key
                # L> For future filtering based off of keywords
                href: AttributeValueList | str | None = anchor.get('href')
                if not isinstance(href, str):
                    continue
                href = Href(href.strip())
                text = AnchorText(anchor.get_text().strip())
                
                if self.processor.is_url(href):
                    # The AnchorText is the key because one link can have multiple anchor texts (rare for the opposite)
                    # L> The opposite should be accounted for in future versions
                    urls[text] = href

            except Exception: 
                continue

        return urls
    
    def extract(self, soup:BeautifulSoup) -> dict[AnchorText, Href]:
        anchors: ResultSet[NavigableString | PageElement | Tag] = self._get_all_anchors(soup)
        return self._filter_valid_urls(anchors)