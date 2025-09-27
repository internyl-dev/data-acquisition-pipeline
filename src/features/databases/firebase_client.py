
import os
import dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

dotenv.load_dotenv()

class FirebaseClient:
    def __init__(self):

        # Replace with the actual path
        cred = credentials.Certificate(os.environ.get("FIREBASE_SDK_PATH"))
        firebase_admin.initialize_app(cred)

        # Get a Firestore client
        self.database = firestore.client()

        #self.logger.debug("Firebase Admin SDK initialized and Firestore client ready!")

    def add_new_data(self, collection_name: str, data: dict):
        """
        Adds a new document to a specified collection with an auto-generated ID.
        Returns `None` and logs an error if it fails to add the document.

        Args:
            collection_name (str): Name of collection in Firestore
            data (dict): Data to add
        """
        try:
            # Get a reference to the collection
            collection_ref = self.database.collection(collection_name)

            # Add the document
            update_time, doc_ref = collection_ref.add(data)

            #self.logger.debug(f"Document added with ID: {doc_ref.id} at {update_time}")
            return doc_ref.id
        
        except Exception as e:
            #self.logger.error(f"Error adding document: {e}")
            return None
