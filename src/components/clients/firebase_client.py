
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class FirebaseClient:
    def __init__(self):

        # Replace with the actual path
        cred = credentials.Certificate("")
        firebase_admin.initialize_app(cred)

        # Get a Firestore client
        self.database = firestore.client()

        print("Firebase Admin SDK initialized and Firestore client ready!")

    def add_new_data(self, collection_name: str, data: dict):
        """Adds a new document to a specified collection with an auto-generated ID."""
        try:
            # Get a reference to the collection
            collection_ref = self.database.collection(collection_name)

            # Add the document
            update_time, doc_ref = collection_ref.add(data)

            print(f"Document added with ID: {doc_ref.id} at {update_time}")
            return doc_ref.id
        
        except Exception as e:
            print(f"Error adding document: {e}")
            return None
