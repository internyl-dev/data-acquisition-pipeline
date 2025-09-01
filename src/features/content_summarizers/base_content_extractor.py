
from abc import ABC, abstractmethod

class ContentExtractor(ABC):
    @abstractmethod
    def extract(s:str):
        "Extracts for some information in a string"