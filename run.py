
from src.main import Main
from src.components.lib.logger import logger
import json
from pprint import pp

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.qcc.cuny.edu/admissions/summerhs.html')
logger.info(json.dumps(Instance.response, indent=1))
pp(Instance.response)