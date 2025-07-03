
from lib.scrape_html import get_html, truncont, is_link
import asyncio
from bs4 import BeautifulSoup
import re
from lib.keywords import keywords
from lib.client import ask_llama, create_prompt
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
    def __init__(self):
        self.history = []
        self.queue = {}
        with open('main/lib/schemas.json', 'r', encoding='utf-8') as file:
            schema = json.load(file)
            self.resp = schema['general-info'] | schema['eligibility'] | schema['dates'] | schema['location'] | schema['cost'] | schema['contact']

    @staticmethod
    def scrape_html(url):
        html = asyncio.run(get_html(url))
        return html

    @staticmethod
    def parse_html(html):
        soup = BeautifulSoup(html, features="html.parser")                # Create bs4 object for external use
        clean_soup = BeautifulSoup(html, features="html.parser")          # Create bs4 object for cleaning

        for tag in clean_soup.find_all(['nav', 'footer']):                # Remove nav and footer tags
            tag.decompose()

        contents = clean_soup.get_text().strip()
        contents = re.sub(r'\n\s*\n+', '\n', contents)                    # Remove repeating new lines
        contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE) # Remove repeating spaces
        
        return soup, contents

    @staticmethod
    def truncate_contents(soup, contents, info, word_limit=1500):
        # Using word count as a rough estimator for token count
        if len(contents.split()) > word_limit:
            return truncont(soup, keywords[info], 1)
        else:
            return contents

    @staticmethod
    def send_request(prompt, context):
        req = create_prompt(prompt)
        resp = ask_llama(context + '\n\n' + req).json()['choices'][0]['message']['content']
        return resp

    @staticmethod
    def get_info_needed(json):
        req = []

        eligibility = json['eligibility']
        if 'not provided' in eligibility['grades'] and list(eligibility['age'].values()) == ['not provided', 'not provided']:
            req.append('eligibility')

        deadlines = json['deadlines']
        if not any([deadline['name'] == 'Application Deadline' for deadline in deadlines]):
            req.append('deadlines')
        
        cost = json['cost']
        if any([plan['free'] == 'not provided' for plan in cost]):
            req.append('cost')
        
        return req

    @staticmethod
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

    @staticmethod
    def filter_links(links, category):
        new_links = {}
        for content in links:
            for keyword in keywords['link'][category]:

                # If the keyword was found in the content, add it to the new dictionary
                if bool(re.search(re.compile(fr'{keyword}', re.I), content)):
                    new_links[content] = links[content]
        
        return new_links
    
    def run(self, url, depth=2):
        
        # If URL was already scraped, end recursion
        # If recursion was not ended, add url to history
        if url in self.history:
            print(f'''
                  #====================#
                  # ALREADY IN HISTORY #
                  #====================#
                  Final depth: {depth}
                  History: {self.history}
                  URL: {url}
                  ''')
            return
        self.history.append(url)

        # If max depth was reached, end recursion
        if depth <= 0:
            print(f'''
                  #===============================#
                  # MAX RECURSION REACHED: ENDING #
                  #===============================#
                  Final depth: {depth}
                  History: {self.history}
                  URL: {url}
                  ''')
            return

        # If all vital info was found, end recursion (this will end recursion for all other cases)
        info_needed = self.get_info_needed(self.resp)
        if not info_needed:
            print(f'''
                  #=============================#
                  # NO MORE INFO NEEDED: ENDING #
                  #=============================#
                  Final depth: {depth}
                  History: {self.history}
                  URL: {url}
                  ''')
            return
        
        #print('\n\n#'+'='*5 +'# ' + 'INFO NEEDED (0)' + ' #'+'='*5 +'#')
        #pprint(info_needed)

        # Scrape HTML from URL
        html = self.scrape_html(url)
        soup, contents = self.parse_html(html)
        #print('\n\n#'+'='*5 +'# ' + 'CONTENTS' + ' #'+'='*5 +'#')
        #pprint(contents)

        # Send AI a POST request asking to fill out schema chunks and update full schema
        # Also remove url from self.queue
        if url in self.queue:
            for info in self.queue[url]:
                context = self.truncate_contents(soup, contents, self.queue[info])
                #self.resp.update(self.send_request(info, context))
            self.queue.pop(url)
        else:
            for info in info_needed:
                context = self.truncate_contents(soup, contents, info)
                #self.resp.update(self.send_request(info, context))
        
        info_needed = self.get_info_needed(self.resp)
        print('\n\n#'+'='*5 +'# ' + 'INFO NEEDED (1)' + ' #'+'='*5 +'#')
        pprint(info_needed)

        new_links = self.get_links(soup)

        for info in info_needed:
            filtered_links = self.filter_links(new_links, info)
            for link in filtered_links.values():
                if link in self.queue:
                    self.queue[link].append(info)
                else:
                    self.queue[link] = [info]
            
            print('\n#'+'='*3 +'# ' + info + ' #'+'='*3 +'#')
            pprint(self.queue)

        # recurse here
        
        return
            

Instance = Main()
Instance.run('https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/')