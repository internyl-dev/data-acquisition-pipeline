
from pprint import pp

from src.main import Main
from src.features.databases import FirebaseClient

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://saldef.org/regionalintern/')
pp(Instance.schema.model_dump())

# Call the function to add it to the 'products' collection
db = FirebaseClient.get_instance()
db.save("demo-history", Instance.schema.model_dump(), set_index=True)