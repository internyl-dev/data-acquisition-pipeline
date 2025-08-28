
from bs4 import BeautifulSoup

class HTMLParser:
    def parse(self, raw_html:str):
        return BeautifulSoup(raw_html, features="html.parser")