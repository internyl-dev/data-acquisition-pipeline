
from pprint import pp

from src.main import Main
from src.io import FirebaseClient

Pipeline = Main(log_mode=True)

db: FirebaseClient = FirebaseClient.get_instance()

# Input link to extract info from
links = db.get_all_data("scrape-queue")
#Pipeline.run(list(links.values())[0]["url"])
Pipeline.run("https://k12stem.engineering.nyu.edu/programs/c-path")
schema = Pipeline.schema.model_dump()
pp(schema)

# Call the function to add it to the 'products' collection
db.save("programs-display", schema, set_index=True)
#db.delete_by_id("scrape-queue", list(links.keys())[0])