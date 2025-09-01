
from abc import ABC, abstractmethod
import logging

class Observer(ABC):
    def update(self, level, *args):
        "Handle updating the observer based on the level and mesage"