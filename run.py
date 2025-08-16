
from src.main import Main
import json

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.awesomemath.org/summer-program/overview/program-information/')
Instance.logger.info('Final extracted info:')
Instance.logger.info(json.dumps(Instance.response, indent=1))
Instance.cleanup_main()

# Call the function to add it to the 'products' collection
reference_id = Instance.add_new_data("internships-history", Instance.response)
if reference_id:
    print(f"New reference ID: {reference_id}")