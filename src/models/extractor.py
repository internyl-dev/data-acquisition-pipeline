
from abc import ABC, abstractmethod

class Extractor(ABC):
    @abstractmethod
    def extract(s:str):
        "Extracts for some information in a string"