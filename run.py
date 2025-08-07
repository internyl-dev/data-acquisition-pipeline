
from src.main import Main
from src.components.lib.logger import logger
import json
from pprint import pp

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.metmuseum.org/about-the-met/internships/high-school')
logger.info(json.dumps(Instance.response, indent=1))
pp(Instance.response)



import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Replace with the actual path
cred = credentials.Certificate('')
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

print("Firebase Admin SDK initialized and Firestore client ready!")

def add_new_data(collection_name: str, data: dict):
    """Adds a new document to a specified collection with an auto-generated ID."""
    try:
        # Get a reference to the collection
        collection_ref = db.collection(collection_name)

        # Add the document
        update_time, doc_ref = collection_ref.add(data)

        print(f"Document added with ID: {doc_ref.id} at {update_time}")
        return doc_ref.id
    
    except Exception as e:
        print(f"Error adding document: {e}")
        return None

# Call the function to add it to the 'products' collection
reference_id = add_new_data("internships-history", Instance.response)
if reference_id:
    print(f"New reference ID: {reference_id}")