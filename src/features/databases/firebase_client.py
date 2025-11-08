
import os
import dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import Self

from src.models import BaseSchemaSection

dotenv.load_dotenv()

class FirebaseClient:
    __shared_instance = None

    def __init__(self):

        if FirebaseClient.__shared_instance:
            raise Exception("Shared instance already exists")

        # Replace with the actual path
        cred = credentials.Certificate(os.environ.get("FIREBASE_SDK_PATH"))
        firebase_admin.initialize_app(cred)

        # Get a Firestore client
        self.database = firestore.client()

        FirebaseClient.__shared_instance = self

        #self.logger.debug("Firebase Admin SDK initialized and Firestore client ready!")

    @classmethod
    def get_instance(cls) -> Self:
        if not cls.__shared_instance:
            cls()
        return cls.__shared_instance
        
    def _get_name_index(self, collection_path:str, document:dict|BaseSchemaSection):
        if isinstance(document, dict):
            link = document["overview"]["link"].replace("/", "\\")
        elif isinstance(document, BaseSchemaSection):
            link = document.overview.link.replace("/", "\\")
        else:
            raise "Document is neither a dictionary nor a BaseSchemaSection"

        documents = self.get_all_data(collection_path)
        documents_with_link = [doc for doc in documents if link in doc]
        
        if not documents_with_link:
            next_index = 0
        else:
            indexes = [int(doc[-1]) for doc in documents_with_link]
            next_index = max(indexes) + 1
        
        return f"{link}-{next_index}"

    def save(self, collection_path:str, document:dict|BaseSchemaSection, set_index:bool=False):
        try:
            collection_ref = self.database.collection(collection_path)
            if set_index:
                document_name = self._get_name_index(collection_path, document)
                collection_ref.document(document_name).set(document)
            else:
                update_item, doc_ref = collection_ref.add(document)

        except Exception as e:
            raise e

    def set(self, id:str, document:dict|BaseSchemaSection):
        pass

    def get_by_id(self, id:str):
        pass

    def get_all_data(self, collection_path:str):
        collection_ref = self.database.collection(collection_path)
        documents = collection_ref.stream()

        return {document.id: document.to_dict() for document in documents}

    def delete_by_id(self, id:str):
        pass

