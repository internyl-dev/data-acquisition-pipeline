
import logging
from src.features.logger import Logger, Observable

class Adder(Observable):
    def __init__(self):
        super().__init__()
        self.sum = 0

    def add(self, x:int, y:int):
        self.sum = x + y
        self.update(x, "and", y, "summed to", self.sum)

adder = Adder()
log = Logger(log_mode=True)
log.apply_conditional_logging()

adder.register(log)
adder.add(3, 4)

log.update({"test": "dict"}, logging.INFO)