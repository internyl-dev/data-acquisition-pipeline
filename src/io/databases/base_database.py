
from abc import ABC, abstractmethod
from src.models import BaseSchemaSection

class DatabaseManager(ABC):
    @abstractmethod
    def save(self, collection_path:str, document:dict|BaseSchemaSection):
        "Saves data to the database"

    @abstractmethod
    def set(self, id:str, document:dict|BaseSchemaSection):
        "Saves data to the database with a specified ID"
    
    @abstractmethod
    def get_by_id(self, id:str):
        "Get a data entry by its ID"

    @abstractmethod
    def get_all_data(self, collection_path:str):
        "Gets all the data in a specific section in a database"

    @abstractmethod
    def delete_by_id(self, id:str):
        "Deletes data associated with an ID"