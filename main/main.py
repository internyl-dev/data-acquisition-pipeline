
from lib.scrape_html import get_html, truncont, is_link
import asyncio
from bs4 import BeautifulSoup
import re
from lib.keywords import keywords
from lib.client import ask_llama, create_prompt
from lib.read_json import get_info_needed
import json
from pprint import pprint

import time
def stopwatch(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f'{func.__name__}:', round(time.time() - start, 2), 'seconds')
        return result
    return wrapper

#======================#
# Scrape HTML contents #
#======================#
@stopwatch
def scrape_html(url):
    html = asyncio.run(get_html(url))
    return html

html = scrape_html('https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/')



#==========================================#
# Prime html contents for parsing with BS4 #
#==========================================#
def parse_html(html):
    soup = BeautifulSoup(html, features="html.parser")                # Create bs4 object for external use
    clean_soup = BeautifulSoup(html, features="html.parser")          # Create bs4 object for cleaning

    for tag in clean_soup.find_all(['nav', 'footer']):                # Remove nav and footer tags
        tag.decompose()

    contents = clean_soup.get_text().strip()
    contents = re.sub(r'\n\s*\n+', '\n', contents)                    # Remove repeating new lines
    contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE) # Remove repeating spaces
    
    return soup, contents

soup, contents = parse_html(html)
pprint(contents)



#==========================================================================================#
# Truncate the html contents for keywords and get the top and bottom lines to make context #
#==========================================================================================#
def truncate_contents(soup, contents, info, word_limit=1500):
    # Using word count as a rough estimator for token count
    if len(contents.split()) > word_limit:
        return truncont(soup, keywords[info], 1)
    else:
        return contents
    
context = truncate_contents(soup, contents, 'cost')
print('\nContext:', context, '\n')



#=======================================================================================#
# Send POST request to local server and receive response as the contents fo a JSON file #
#=======================================================================================#
@stopwatch
def send_request(prompt, context):
    req = create_prompt(prompt)
    resp = ask_llama(context + '\n\n' + req).json()['choices'][0]['message']['content']
    return resp

#resp = send_request('general-info', context)
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
  "cost": [
      {
        "name": "not provided",
        "free": "not provided",
        "lowest": "not provided",
        "highest": "not provided",
        "financial-aid-available": "not provided"
      }
    ],
  "stipend": {
    "available": "not provided",
    "amount": "not provided"
  },
  "contact": {
    "email": "not provided",
    "phone": "not provided"
  }
}



#================================================#
# Determine whether or not vital info is missing #
#================================================#
info_needed = get_info_needed(resp)
print('Info needed:', info_needed, '\n')



#=======================================#
# Find other links from within the HTML #
#=======================================#
def get_links(soup):
    new_links = {}
    links = soup.find_all('a')         # Gets all anchor elements

    for link in links:
        url = link.get('href')
        text = link.get_text().strip() # Remove repeating indents and spaces

        try:
            if is_link(url):           # Finds out if the href is a valid link or not
                new_links[text] = url
        except Exception: 
            pass

    return new_links

new_links = get_links(soup)
pprint(new_links)
print('\n')



#===============================================#
# Find keywords in link for specific categories #
#===============================================#
def filter_links(links, category):
    new_links = {}
    for content in links:
        for keyword in keywords['link'][category]:

            # If the keyword was found in the content, add it to the new dictionary
            if bool(re.search(re.compile(fr'{keyword}', re.I), content)):
                new_links[content] = links[content]
    
    return new_links

filtered_links = filter_links(new_links, 'cost')
pprint(filtered_links)



# scrape_html(url)
# parse_html(html)
# truncate_contents(soup, contents, word_count)
# send_request(prompt, context)
# get_info_needed(resp)
# get_links(soup)
# filter_links(links, category)

# Starting from webpage 1:
# 1. scrape
# 2. parse
# 3. truncate
# 4. send request
# -> global resp
# -> add previous JSON for context if needed
# 5. check info needed
# -> info needed: go to step 6
# -> info not needed: end
# 6. get links
# 7. filter links for info in info needed
# 8. for link in links, repeat from step 1 minus one recursion

class Main:
    def __init__(self, url):
        self.history = [url]
        self.queue = [url]
        with open('lib/schemas.json', 'r', encoding='utf-8') as file:
            self.resp = json.load(file)['full']
    
    def run(self, depth):
        if depth <= 0:
            return

        info_needed = get_info_needed(self.resp)
        if not info_needed:
            return

        html = scrape_html(self.url)
        soup, contents = parse_html(html)

        for info in info_needed:
            context = truncate_contents(soup, contents, info)
            self.resp = send_request(info, context)
        
        info_needed = get_info_needed(self.resp)

        new_links = get_links(soup)

        for info in info_needed:
            filtered_links = filter_links(new_links, info)
            # loop through links and call run recursively