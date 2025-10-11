
from pprint import pp

from src.main import Main
from src.features.databases import FirebaseClient

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.amnh.org/learn-teach/teens/saltz-internship-program')
pp(Instance.schema.model_dump())

# Call the function to add it to the 'products' collection
db = FirebaseClient()
db.save("programs-display", Instance.schema.model_dump(), set_index=True)