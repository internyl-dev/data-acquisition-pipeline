
from abc import ABC, abstractmethod

class DatabaseManager(ABC):
    @abstractmethod
    def save(self, data:dict):
        "Saves data to the database"

    @abstractmethod
    def set(self, id:str, data:dict):
        "Saves data to the database with a specified ID"
    
    @abstractmethod
    def get_by_id(self, id:str):
        "Get a data entry by its ID"

    @abstractmethod
    def get_all_data(self):
        "Gets all the data in a specific section in a database"

    @abstractmethod
    def delete_by_id(self, id:str):
        "Deletes data associated with an ID"