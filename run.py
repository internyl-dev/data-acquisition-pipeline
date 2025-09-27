
from pprint import pp

from src.main import Main
from src.features.databases import FirebaseClient

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.nyhistory.org/education/student-historian-internship-program')
#Instance.logger.info('Final extracted info:')
#Instance.logger.info(json.dumps(Instance.response, indent=1))
pp(Instance.schema.model_dump())

# Call the function to add it to the 'products' collection
db = FirebaseClient()
reference_id = db.add_new_data("programs-display", Instance.schema.model_dump())
if reference_id:
    print(f"New reference ID: {reference_id}")