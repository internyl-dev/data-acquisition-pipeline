
from pprint import pp

from src.main import Main
from src.features.databases import FirebaseClient

Pipeline = Main(log_mode=False)
Pipeline2 = Main(log_mode=False)

db: FirebaseClient = FirebaseClient.get_instance()

# Input link to extract info from
links = db.get_all_data("scrape-queue")
Pipeline.run(list(links.values())[0]["url"])
Pipeline2.run(list(links.values())[1]["url"])
schema = Pipeline.schema.model_dump()
schema2 = Pipeline2.schema.model_dump()
pp(schema)
pp(schema2)

# Call the function to add it to the 'products' collection
db.save("programs-display", schema, set_index=True)
db.save("programs-display", schema2, set_index=True)
db.delete_by_id("scrape-queue", list(links.keys())[0])
db.delete_by_id("scrape-queue", list(links.keys())[1])