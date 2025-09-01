
import re
from bs4 import BeautifulSoup

from .base_html_cleaner import HTMLCleaner

class HTMLDeclutterer(HTMLCleaner):
    def _remove_navigation(self, soup:BeautifulSoup):
        # headers, navs, and footers typically contain links to other parts of the website
        # L> Excessively clutter context, especially when truncating for keywords
        for element in ['header', 'nav', 'footer']:
            elements = soup.find_all(element)  
            for elm in elements:
                elm.decompose()

        return soup

    def _remove_forms(self, soup:BeautifulSoup):
        # These are all common form elements that can have text
        # Often contain tens of options that just clutter context
        for element in ['select', 'textarea', 'button', 'option']:
            elements = soup.find_all(element)
            for elm in elements:
                elm.decompose()

        return soup

    def clean(self, soup:BeautifulSoup):
        """
        Removes all HTML elements from BeautifulSoup object that would clutter the page contents.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            soup (BeautifulSoup): HTML contents with cluttering elements removed
        """
        soup = self._remove_navigation(soup)
        soup = self._remove_forms(soup)
        
        return soup



class HTMLWhitespaceCleaner(HTMLCleaner):
    def clean(self, soup:BeautifulSoup):
        """
        Removes excessive white space from a string.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page
        
        Returns:
            contents (str): Webpage contents as a string without excessive white space.
        """
        contents = soup.get_text()

        # Remove excessive white space
        contents = re.sub(r'\n\s*\n+', '\n', contents)
        contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE)

        return contents