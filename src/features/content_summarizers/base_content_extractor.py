
from abc import ABC, abstractmethod

class ContentExtractor(ABC):
    @staticmethod
    @abstractmethod
    def extract(s:str) -> list[str]:
        "Extracts for some information in a string"