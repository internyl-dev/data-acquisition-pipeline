
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class QueueStrategy(ABC, Generic[T]):
    def __init__(self, items: list) -> None:
        self._items = items
    
    @abstractmethod
    def add(self, item) -> None:
        "Add an item following the strategy."

    @abstractmethod
    def get(self) -> Optional[T]:
        "Get an item following the strategy and delete it from storage."

    @abstractmethod
    def peek(self) -> Optional[T]:
        "Return the value of an item following the strategy without deletion."

class FIFO(QueueStrategy[T]):
    """
    First in, first out strategy.
    """
    def add(self, item:T) -> None:
        self._items.append(item)
    
    def get(self) -> Optional[T]:
        return self._items.pop(0) if self._items else None
    
    def peek(self) -> Optional[T]:
        return self._items[0] if self._items else None

class FILO(QueueStrategy[T]):
    """
    First in, last out strategy.
    """
    def add(self, item) -> None:
        self._items.append(item)
    
    def get(self) -> Optional[T]:
        return self._items.pop() if self._items else None
    
    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None