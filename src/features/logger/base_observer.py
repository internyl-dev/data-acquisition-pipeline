
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, level, *args):
        "Handle updating the observer based on the level and mesage"