
import unittest
from bs4 import BeautifulSoup

from src.features.web_crawler import URLExtractor, URLFilter, URLProcessor, URLRanker
from src.models import Case

with open(file="tests/test_web_crawler/sample.html", mode="r", encoding="utf-8") as f:
    sample_html = f.read()

class TestWebCrawler(unittest.TestCase):
    def setUp(self):
        self.extractor = URLExtractor()
        self.processor = URLProcessor()

    def test_url_extractor(self):
        cases = [
            [BeautifulSoup(sample_html, "html.parser"),
             {'About': '/about', 
              'link': '/more', 
              'Partner Resources': 'https://www.partner.com/resources', 
              'Tutorials': 'https://www.docs.example.com/tutorials', 
              'FAQ': '/faq'}],

            [BeautifulSoup("", "html.parser"),
             {}]
        ]

        for case in cases:
            self.assertEqual(
                self.extractor.extract(case[0]), case[1]
            )

    def test_url_processor(self):
        cases = [
            {"args": ["https://www.example.com/", "/about"],
             "outp": "https://www.example.com/about"},

            {"args": ["https://www.example.com/", "https://www.anothersite.com/"],
             "outp": "https://www.anothersite.com/"}
        ]

        for case in cases:
            self.assertEqual(
                self.processor.process_url(case["args"][0], case["args"][1]), case["outp"]
            )
    
    def test_url_filter(self):
        cases = [
            Case()
        ]

unittest.main()