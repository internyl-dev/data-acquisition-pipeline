
import time
def stopwatch(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f'{func.__name__}:', round(time.time() - start, 2), 'seconds')
        return result
    return wrapper

from lib.scrape_html import get_html, truncont, is_link
import asyncio
from bs4 import BeautifulSoup
import re
from lib.keywords import keywords
from main.lib.client import ask_llama, create_prompt
from lib.read_json import get_info_needed
import pprint

# Scrape HTML contents
@stopwatch
def scrape_html(url):
    html = asyncio.run(get_html(url))
    return html
html = scrape_html('https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/')



# Prime html contents for parsing with BS4
def parse_html(html):
    global soup
    soup = BeautifulSoup(html, features="html.parser")
    contents = soup.get_text().strip()
    contents = re.sub(r'\n\s*\n+', '\n', contents) # Remove repeating new lines
    contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE) # Remove repeating spaces
    return contents
contents = parse_html(html)
#print(contents)



# Truncate the html contents for keywords and get the top and bottom lines to make context
context = truncont(soup, keywords['kw_eligibility'], 1)
#print('Context:', context.split('\n'))



# Send POST request to local server and receive response as the contents fo a JSON file
@stopwatch
def send_request(prompt):
    req = create_prompt(prompt)
    resp = ask_llama(context + '\n\n' + req).json()['choices'][0]['message']['content']
    return resp
#resp = send_request('general-info')

resp = {
  "title": "not provided",
  "provider": "not provided",
  "description": "not provided",
  "link": "not provided",
  "subjects": [],
  "tags": [],
  "requirements": {
    "essay_required": "not provided",
    "recommendation_required": "not provided",
    "transcript_required": "not provided",
    "other": []
  },
  "eligibility": {
    "grades": 'not provided',
    "age": {
      "minimum": "not provided",
      "maximum": "not provided"
    }
  },
  "deadlines": [],
  "dates": [],
  "duration_weeks": "not provided",
  "location": [],
  "cost": [],
  "stipend": {
    "available": "not provided",
    "amount": "not provided"
  },
  "contact": {
    "email": "not provided",
    "phone": "not provided"
  }
}



# Determine whether or not vital info is missing
info_needed = get_info_needed(resp)
#print('Info needed:', info_needed)



# Find other links from within the HTML
def get_links(soup):
    new_links = {}
    links = soup.find_all('a')
    for link in links:
        url = link.get('href')
        text = link.get_text().strip()

        try:
            if is_link(url):
                new_links[text] = url
        except:
            pass

    return new_links

new_links = get_links(soup)
pprint.pprint(new_links)