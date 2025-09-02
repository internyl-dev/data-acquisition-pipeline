
from pydantic import BaseModel
from .queue_strategies import QueueStrategy, FIFO, FILO

class QueueItem(BaseModel):
    url: str
    target_fields: list[str]
    priority: int=0
    
class Queue:
    def __init__(self, strat:QueueStrategy=None):
        self.items = []
        self.default_strat = strat or FIFO

    def add(self, item:QueueItem, strat:QueueStrategy=None):
        strat = strat or self.default_strat
        strat_obj = strat(self.items)
        strat_obj.add(item)
        self.items = strat_obj._items

    def get(self, strat:QueueStrategy=None):
        strat = strat or self.default_strat
        strat_obj = strat(self.items)
        item = strat_obj.get()
        self.items = strat_obj._items
        return item
    
    def peek(self, strat:QueueStrategy=None):
        strat = strat or self.default_strat
        strat_obj = strat()
        item = strat_obj.peek()
        return item


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