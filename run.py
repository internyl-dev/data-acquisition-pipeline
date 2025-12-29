
from pprint import pp

from src.main import Main
from src.io import FirebaseClient

Pipeline = Main(log_mode=True)

db: FirebaseClient = FirebaseClient.get_instance()

# Input link to extract info from
links = db.get_all_data("scrape-queue")
#Pipeline.run(list(links.values())[0]["url"])
links = [
    "https://www.nyhistory.org/education/student-historian-internship-program"
]
for link in links:
    Pipeline.run(link)
    schema = Pipeline.schema.model_dump()
    db.save("programs-display", schema, set_index=True)
    Pipeline.clear()

# Call the function to add it to the 'products' collection
#db.save("programs-display", schema, set_index=True)
#db.delete_by_id("scrape-queue", list(links.keys())[0])