
from abc import ABC, abstractmethod

class QueueStrategy(ABC):
    def __init__(self, items):
        self._items = items
    
    @abstractmethod
    def add(self, items):
        "Add an item following the strategy."

    @abstractmethod
    def get(self):
        "Get an item following the strategy and delete it from storage."

    @abstractmethod
    def peek(self):
        "Return the value of an item following the strategy without deletion."

class FIFO(QueueStrategy):
    """
    First in, first out strategy.
    """
    def add(self, item):
        self._items.append(item)
    
    def get(self):
        return self._items.pop(0) if self._items else None
    
    def peek(self):
        return self._items[0] if self._items else None

class FILO(QueueStrategy):
    """
    First in, last out strategy.
    """
    def add(self, item):
        self._items.append(item)
    
    def get(self):
        return self._items.pop() if self._items else None
    
    def peek(self):
        return self._items[-1] if self._items else None