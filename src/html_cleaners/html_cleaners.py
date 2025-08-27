
import re
from bs4 import BeautifulSoup

from src.models import HTMLCleaner

class HTMLDeclutterer(HTMLCleaner):
    def _remove_navigation(self, soup:BeautifulSoup):
        # headers, navs, and footers typically contain links to other parts of the website
        # L> Excessively clutter context, especially when truncating for keywords
        for element in ['header', 'nav', 'footer']:
            elements = soup.find_all(element)  
            for elm in elements:
                elm.decompose()

    def _remove_forms(self, soup:BeautifulSoup):
        # These are all common form elements that can have text
        # Often contain tens of options that just clutter context
        for element in ['select', 'textarea', 'button', 'option']:
            elements = soup.find_all(element)
            for elm in elements:
                elm.decompose()

    def clean(self, soup:BeautifulSoup):
        """
        Removes all HTML elements from BeautifulSoup object that would clutter the page contents.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            soup (BeautifulSoup): HTML contents with cluttering elements removed
        """
        soup = self._remove_navigation()
        soup = self._remove_forms()
        
        return soup
    

class HTMLWhitespaceCleaner(HTMLCleaner):
    def clean(self, soup:BeautifulSoup):
        """
        Converts a BeautifulSoup object to a string while also removing excessive white space from the string.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page
        
        Returns:
            contents (str): Webpage contents as a string without excessive white space.
        """

        # Remove excessive white space
        contents = soup.get_text().strip()
        contents = re.sub(r'\n\s*\n+', '\n', contents)
        contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE)

        return contents