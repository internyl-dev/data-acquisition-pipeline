
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def log(self, level, message):
        "Logs a message to their corresponding endpoints"