
import unittest
from bs4 import BeautifulSoup

from src.features.html_cleaners import HTMLDeclutterer, HTMLWhitespaceCleaner

with open(file="tests/test_html_cleaners/sample.html", mode="r", encoding="utf-8") as f:
    sample_html = f.read()

class TestHTMLCleaner(unittest.TestCase):
    def test_declutterer(self):
        raw_soup = BeautifulSoup(sample_html, "html.parser")
        declutterer = HTMLDeclutterer()
        
        soup = declutterer.clean(raw_soup)

        for elm in ['header', 'nav', 'footer', 'select', 'textarea', 'button', 'option']:
            self.assertFalse(
                soup.find_all(elm)
            )

    def test_whitespace_cleaner(self):
        raw_soup = BeautifulSoup(sample_html, "html.parser")
        whitespace_cleaner = HTMLWhitespaceCleaner()

        contents = whitespace_cleaner.clean(raw_soup)
        lines = contents.split('\n')

        self.assertFalse(
            any([a==None and b==None for a, b in zip(lines, lines[1:])])
        )

unittest.main()