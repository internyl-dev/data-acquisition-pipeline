
from pydantic import BaseModel
from .queue_strategies import QueueStrategy, FIFO, FILO

class QueueItem(BaseModel):
    """
    A URL object that contains important information like:
    - The URL
    - The target fields
    - The scraping priority
    """
    url: str
    target_fields: list[str]
    priority: int=0
    
class Queue:
    """
    A container object that represents the queue of oncoming
    objects to be scraped. Items can be deleted after being
    added unlike with the `History` object.
    \n
    A queue strategy can be added upon instantiation to
    determine the behavior of the queue methods.
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

    def get(self, strat:QueueStrategy=None) -> any:
        """
        Returns an item from the queue given a strategy
        along with its deletion.
        """
        strat = strat or self.default_strat
        strat_obj = strat(self.items)
        item = strat_obj.get()
        self.items = strat_obj._items
        return item
    
    def peek(self, strat:QueueStrategy=None) -> any:
        "Returns an item from the queue without deletion."
        strat = strat or self.default_strat
        strat_obj = strat()
        item = strat_obj.peek()
        return item

    def is_in(self, item:QueueItem):
        """
        Checks whether or not an item is in storage. The
        item has to be an object reference and will check
        whether or not it is in storage based on the __eq__
        method.
        \n
        **TLDR**; If an equivalent item is in storage, it'll
        return `True`.

        Args:
            item (any): The item to check.
        """
        return (item in self.items)

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