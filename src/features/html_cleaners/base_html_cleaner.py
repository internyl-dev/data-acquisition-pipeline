
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class HTMLCleaner(ABC):
    @abstractmethod
    def clean(self, soup:BeautifulSoup):
        "Cleans parsed HTML contents"