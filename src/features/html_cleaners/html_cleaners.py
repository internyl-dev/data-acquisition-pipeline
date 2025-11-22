
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass

from .base_html_cleaner import HTMLCleaner

@dataclass
class HTMLDeclutterer(HTMLCleaner):
    remove_header:bool=True,
    remove_nav:bool=True,
    remove_footer:bool=True
    remove_select:bool=True
    remove_textarea:bool=True
    remove_button:bool=True
    remove_option:bool=True

    @staticmethod
    def _remove_element(element:str, soup:BeautifulSoup):
        elements = soup.find_all(element)
        
        # No elements found
        if not elements:
            return soup
        
        # Remove all found elements
        for elm in elements:
            elm.decompose()
        
        return soup
    
    def _remove_header(self, soup:BeautifulSoup):
        return self._remove_element('header', soup)

    def _remove_nav(self, soup:BeautifulSoup):
        return self._remove_element('nav', soup)

    def _remove_footer(self, soup:BeautifulSoup):
        return self._remove_element('footer', soup)

    def _remove_navigation(self, soup:BeautifulSoup):
        # headers, navs, and footers typically contain links to other parts of the website
        # L> Excessively clutter context, especially when truncating for keywords
        soup = self._remove_header(soup) if self.remove_header else soup
        soup = self._remove_nav(soup) if self.remove_nav else soup
        soup = self._remove_footer(soup) if self.remove_footer else soup

        return soup
    
    def _remove_select(self, soup:BeautifulSoup) -> BeautifulSoup:
        return self._remove_element('select', soup)
    
    def _remove_textarea(self, soup:BeautifulSoup) -> BeautifulSoup:
        return self._remove_element('textarea', soup)
    
    def _remove_button(self, soup:BeautifulSoup) -> BeautifulSoup:
        return self._remove_element('button', soup)
    
    def _remove_option(self, soup:BeautifulSoup) -> BeautifulSoup:
        return self._remove_element('option', soup)

    def _remove_forms(self, soup:BeautifulSoup) -> BeautifulSoup:
        # These are all common form elements that can have text
        # Often contain tens of options that just clutter context
        self._remove_select(soup) if self.remove_select else soup
        self._remove_textarea(soup) if self.remove_textarea else soup
        self._remove_button(soup) if self.remove_button else soup
        self._remove_option(soup) if self.remove_option else soup

        return soup

    def clean(self, soup:BeautifulSoup) -> BeautifulSoup:
        """
        Removes all HTML elements from BeautifulSoup object that would clutter the page contents.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            soup (BeautifulSoup): HTML contents with cluttering elements removed
        """
        self._remove_navigation(soup)
        self._remove_forms(soup)
        
        return soup



class HTMLWhitespaceCleaner(HTMLCleaner):
    def clean(self, soup:BeautifulSoup) -> BeautifulSoup:
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