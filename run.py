
from src.main import Main

Instance = Main(log_mode=True)

# Input link to extract info from
Instance.run('https://www.metmuseum.org/about-the-met/internships/high-school/summer-high-school-internships')
print(Instance.response)