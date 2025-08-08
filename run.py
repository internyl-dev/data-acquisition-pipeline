
from src.main import Main
import json
from pprint import pp

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.metmuseum.org/about-the-met/internships/high-school/school-year-high-school-internships')
Instance.logger.info(json.dumps(Instance.response, indent=1))
pp(Instance.response)

# Call the function to add it to the 'products' collection
reference_id = Instance.add_new_data("internships-history", Instance.response)
if reference_id:
    print(f"New reference ID: {reference_id}")