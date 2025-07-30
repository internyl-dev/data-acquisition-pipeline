
from src.main import Main

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/')
Instance.log(Instance.response)