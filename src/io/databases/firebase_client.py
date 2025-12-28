
import os
import dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import Self, Optional

from src.models import RootSchema

dotenv.load_dotenv()

class FirebaseClient:
    __shared_instance:Optional[Self] = None

    def __init__(self) -> None:

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
        assert cls.__shared_instance
        return cls.__shared_instance
        
    def _get_name_index(self, collection_path:str, document:dict|RootSchema) -> str:
        if isinstance(document, dict):
            link = document["overview"]["link"].replace("/", "\\")
        elif isinstance(document, RootSchema):
            link = document.overview.link.replace("/", "\\")

        documents = self.get_all_data(collection_path)
        documents_with_link = [doc for doc in documents if link in doc]
        
        if not documents_with_link:
            next_index = 0
        else:
            indexes = [int(doc[-1]) for doc in documents_with_link]
            next_index = max(indexes) + 1
        
        return f"{link}-{next_index}"

    def save(self, collection_path:str, document:dict|RootSchema, set_index:bool=False) -> None:
        try:
            collection_ref = self.database.collection(collection_path)

            if isinstance(document, RootSchema):
                document = document.model_dump()

            if set_index:
                document_name = self._get_name_index(collection_path, document)
                collection_ref.document(document_name).set(document)
            else:
                update_item, doc_ref = collection_ref.add(document)

        except Exception as e:
            raise e

    def set(self, id:str, document:dict|RootSchema):
        pass

    def get_by_id(self, id:str):
        pass

    def get_all_data(self, collection_path:str)-> dict:
        collection_ref = self.database.collection(collection_path)
        documents = collection_ref.stream()

        return {document.id: document.to_dict() for document in documents}

    def delete_by_id(self, collection_path:str, id:str) -> None:
        collection_ref = self.database.collection(collection_path)
        collection_ref.document(id).delete()

