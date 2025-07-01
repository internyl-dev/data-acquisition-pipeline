
from lib.scrape_html import get_html
import asyncio

from bs4 import BeautifulSoup
import re
import pyperclip

# Scrape HTML contents
url = 'https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/'
html = asyncio.run(get_html(url))

# Prime html contents for parsing with bs4
soup = BeautifulSoup(html, features="html.parser")
contents = soup.get_text().strip()
contents = re.sub(r'\n\s*\n+', '\n', contents)
#print(contents)
pyperclip.copy(contents)

filename = ';'.join(url.split('//')[1].split('/'))

f = open(f'C:/Users/efrat/Downloads/training_data/sites/{filename}.txt', "w", encoding="utf-8")
f.write(contents)
