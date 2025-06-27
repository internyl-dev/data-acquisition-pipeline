
from lib.scrape_html import get_html
import asyncio

from bs4 import BeautifulSoup
import re
import pyperclip

# Scrape HTML contents
url = 'https://www.americaontech.org/fellowships.html'
html = asyncio.run(get_html(url))

# Prime html contents for parsing with bs4
soup = BeautifulSoup(html, features="html.parser")
contents = soup.get_text().strip()
contents = re.sub(r'\n\s*\n+', '\n', contents)
#print(contents)
pyperclip.copy(contents)

filename = '-'.join(url.split('//')[1].split('/'))

f = open(f'C:/Users/efrat/Downloads/training_data/sites/{filename}.txt', "w", encoding="utf-8")
f.write(contents)



"""from lib.truncate_html import truncont
from lib.keywords import keywords

# Truncate the html contents for keywords and get the top and bottom lines to make context
context = truncont(soup, keywords['kw_deadline'], 1)
print(context.split('\n'))



from lib.llama_client import ask_llama
from lib.prompt import create_prompt
import time

start = time.time()

# general-info, eligibility, dates, location, cost, contact
req = create_prompt('general-info')
print(ask_llama(context + '\n\n' + req).json()['choices'][0]['message']['content'])

print(time.time() - start)
"""