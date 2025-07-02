
import pyperclip
from main import scrape_html
from main import parse_html

url = 'https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/'
html = scrape_html(url)

contents = parse_html(html)
pyperclip.copy(contents)

filename = ';'.join(url.split('//')[1].split('/'))

f = open(f'C:/Users/efrat/Downloads/training_data/sites/{filename}.txt', "w", encoding="utf-8")
f.write(contents)
