
from pydantic import BaseModel
from dataclasses import dataclass
from .queue_strategies import QueueStrategy, FIFO, FILO
from .schema_fields import Fields
from typing import List

@dataclass
class QueueItem:
    """
    A URL object that contains important information like:
    - The URL
    - The target fields
    - The scraping priority
    """
    url: str
    target_fields: list[str | Fields]
    priority: int=0
    
class Queue:
    """
    A container object that represents the queue of oncoming
    objects to be scraped. Items can be deleted after being
    added unlike with the `History` object
    \n
    A queue strategy can be added upon instantiation to
    determine the behavior of the queue methods
    """
    def __init__(self, strat:QueueStrategy=None):
        self.items = []
        self.default_strat = strat or FIFO

    def add(self, item:QueueItem, strat:QueueStrategy=None) -> None:
        "Adds an item to the queue."
        strat = strat or self.default_strat
        strat_obj = strat(self.items)
        strat_obj.add(item)
        self.items = strat_obj._items

    def get(self, strat:QueueStrategy=None) -> QueueItem:
        """
        Returns an item from the queue given a strategy
        along with its deletion.
        """
        strat = strat or self.default_strat
        strat_obj = strat(self.items)
        item = strat_obj.get()
        self.items = strat_obj._items
        return item
    
    def peek(self, strat:QueueStrategy=None) -> QueueItem:
        "Returns an item from the queue without deletion"
        strat = strat or self.default_strat
        strat_obj = strat(self.items)
        item = strat_obj.peek()
        return item

    def is_in(self, item:QueueItem) -> bool:
        """
        Checks whether an item has the same link
        as another item in the current queue
        \n
        Args:
            item (any): The item to check
        """
        items = [item.url for item in self.items]
        return (item.url in items)
    
    def find(self, item:QueueItem) -> QueueItem | None:
        """
        Returns the `QueueItem` object that has the 
        same link as the argument `QueueItem`object
        """
        return next((q_item for q_item in self.items if q_item.url == item.url), None)
    
    def replace(self, item:QueueItem) -> None:
        """
        Replaces the item in the queue that has the same
        link as the argument given with the argument
        """
        q_item = self.find(item)
        if q_item:
            index = self.items.index(q_item)
            self.items[index] = item

    def get_length(self) -> int:
        "Returns the amount of items in the queue"
        return len(self.items)
    
    def get_all_urls(self) -> List[str]:
        "Get all the URLs from each item as a list of strings"
        all_urls = []
        for item in self.items:
            all_urls.append(item.url)
        return all_urls
    
    def keep_urls(self, urls:list) -> None:
        "Delete all queue items that do not have a link in the given list of urls"
        for item in self.items:
            if item.url not in urls:
                self.items.remove(item)

if __name__ == "__main__":

    item1 = QueueItem(url="first", target_fields=["item"])
    item2 = QueueItem(url="second", target_fields=["item"])

    queue = Queue(FIFO)
    queue.add(item1)
    queue.add(item2)

    print(queue.items)

    item = queue.get()
    print(item)

    print(queue.items)

    item3 = QueueItem(url="second", target_fields=["another item"])
    print(queue.is_in(item3))

    queue.replace(item3)
    print(queue.items)

    item4 = QueueItem(url="third", target_fields="yeah")
    item5 = QueueItem(url="fourth", target_fields="yerr")
    queue.add(item4)
    queue.add(item5)

    print(queue.get_all_urls())
    queue.keep_urls(["third", "fourth"])
    print(queue.get_all_urls())
