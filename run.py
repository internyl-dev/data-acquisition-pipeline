
from pprint import pp

from src.main import Main
from src.features.databases import FirebaseClient

Instance = Main(log_mode=True)

db: FirebaseClient = FirebaseClient.get_instance()

# Input link to extract info from
links = db.get_all_data("scrape-queue")
Instance.run(list(links.values())[0]["url"])
pp(Instance.schema.model_dump())

# Call the function to add it to the 'products' collection
db.save("programs-display", Instance.schema.model_dump(), set_index=True)
db.delete_by_id("scrape-queue", list(links.keys())[0])