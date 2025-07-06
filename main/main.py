
from lib.scrape_html import *
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
            self.resp = json.load(file)
        
        self.data = {"messages": [{"role": "user","content": ""},{"role": "assistant","content": {}}]}

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

        for element in ['header', 'footer']:
            elm = soup.find(element)
            if elm:
                elm.decompose()
        
        for element in ['select', 'textarea', 'button', 'option']:
            elements = soup.find_all(element)
            for elm in elements:
                elm.decompose()

        contents = clean_soup.get_text().strip()
        contents = re.sub(r'\n\s*\n+', '\n', contents)                    # Remove repeating new lines
        contents = re.sub(r'^\s+|\s+$', '', contents, flags=re.MULTILINE) # Remove repeating spaces
        
        return soup, contents

    @staticmethod
    def truncate_contents(soup, contents, info, word_limit=1500):
        # Using word count as a rough estimator for token count
        if len(contents.split()) > word_limit and not info == 'overview':
            if info == 'dates':
                kws = keywords[info] + find_dates(contents)
                return truncont(soup, kws, 1)
            elif info == 'contact':
                kws = keywords[info] + find_emails(contents) + find_phone_numbers(contents)
                return truncont(soup, kws, 1)
            else:
                return truncont(soup, keywords[info], 1)
        else:
            return contents

    @staticmethod
    def send_request(prompt, context):
        req = create_prompt(prompt)
        resp = ask_llama(context + '\n\n' + req).json()['choices'][0]['message']['content']
        return resp

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

                # If the keyword was found in the text or HREF, add it to the new dictionary
                if re.search(fr'{keyword}', content, re.I) or re.search(fr'{keyword}', links[content], re.I):
                    new_links[content] = links[content]
        
        return new_links
    
    @staticmethod
    def process_link(url, link):
        if link[0] == '/':
            link = '/'.join(url.split('/')[0:3]) + link

        elif link[0:7] == 'http://' or link[0:8] == 'https://':
            return link

        elif link[-1] == '/':
            if url[-1] == '/':
                url = url[:-1]
            link = url + link

        return link
    
    @staticmethod
    def read_last_jsonl():
        with open("main/data.jsonl", "rb") as f:
            f.seek(0, 2)  # Go to end of file
            pos = f.tell() - 1

            while pos > 0:
                f.seek(pos)
                char = f.read(1)
                if char == b"\n":
                    # Read the next line after newline
                    last_line = f.readline().decode("utf-8").strip()
                    if last_line != '':
                        return json.loads(last_line)
                pos -= 1

            # If we reach start of file, read from beginning (in case single line no newline)
            f.seek(0)
            last_line = f.readline().decode("utf-8").strip()
            return json.loads(last_line)

    def save_to_jsonl(self, context):
        data = self.data.copy()
        data['messages'][0]['content'] = context

        with open("main/data.jsonl", "a+", encoding="utf-8") as file:
            file.write(json.dumps(self.data) + "\n")
            file.flush()

            loops = 0

            c = self.read_last_jsonl()
            while not c['messages'][1]['content']:
                loops += 1
                time.sleep(1)
                c = self.read_last_jsonl()
                print('Read last line', loops, 'time(s)')
        
        return self.read_last_jsonl()['messages'][1]['content']

    def run(self, url, depth=2):
        
        # If URL was already scraped, remove from queue and end recursion
        if url in self.history:
            self.queue.pop(url)
            print(f'''
                  #====================#
                  # ALREADY IN HISTORY #
                  #====================#
                  Final depth: {depth}
                  History: {self.history}
                  URL: {url}
                  ''')
            return
        self.history.append(url)  # If recursion was not ended, add url to history

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
        info_needed = get_info_needed(self.resp)
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
        if url in self.queue:
            # Only sending requests based on self.queue.values() saves time
            for info in self.queue[url]:
                context = self.truncate_contents(soup, contents, info) + f'\n\n{info}'

                #self.resp[info].update(self.send_request(info, context)[info])
            self.queue.pop(url) # Remove from self.queue

        else:
            # The need to check for info as the first loop is redundant, modify later (not top priority)
            for info in info_needed:
                context = self.truncate_contents(soup, contents, info) + f'\n\n{info}'

                self.resp.update({'link': url})
                #self.resp[info].update(self.send_request(info, context)[info])
        
        # Check what other information is needed after contents of current website was evaluated
        info_needed = get_info_needed(self.resp)
        print('\n\n#'+'='*5 +'# ' + 'INFO NEEDED (1)' + ' #'+'='*5 +'#')
        pprint(info_needed)

        # Get all links within HTML
        new_links = self.get_links(soup)
        print('\n\n#'+'='*5 +'# ' + 'UNFILTERED LINKS' + ' #'+'='*5 +'#')
        pprint(new_links)

        # Filter links based on if there are key words in the HREF (has possibility to miss vital links)
        for info in info_needed:
            filtered_links = self.filter_links(new_links, info)
            print('\n\n#'+'='*5 +'# ' + 'FILTERING LINKS' + ' #'+'='*5 +'#')
            pprint(filtered_links)

            for link in filtered_links.values():
                link = self.process_link(url, link)

                # If link is in history, ignore
                if link in self.history:
                    pass

                # If link is already in queue, check if its values already have the info labels
                elif link in self.queue:
                    if not info in self.queue[link]:
                        self.queue[link].append(info)

                # Add link and assign its values with labels based off of what information can be found
                else:
                    self.queue[link] = [info]
        
        print('\n\n#'+'='*5 +'# ' + 'QUEUE' + ' #'+'='*5 +'#')
        for entry in self.queue:
            print(entry, self.queue[entry])

        # Recursion loop runs while there are still links in self.queue
        while self.queue:   
            self.run(list(self.queue.keys())[0])
        
        return
    
    def collect_data(self, url, depth=2):

        # collect_data runs with the same logic as run but doesn't send requests, instead taking user input from the JSONL
        # the difference can be found in the highlighted section of this code
        if url in self.history:
            self.queue.pop(url)
            return
        self.history.append(url)

        if depth <= 0:
            return

        info_needed = get_info_needed(self.resp)
        print(info_needed)
        if not info_needed:
            return

        html = self.scrape_html(url)
        soup, contents = self.parse_html(html)

        #==============================================================================#
        def create_data(soup, contents, info):
                print(url)
                context = self.truncate_contents(soup, contents, info) + f'\n\n{info}'
                response = self.save_to_jsonl(context + '\n'
                                              + self.resp['overview']['title'] + '\n'
                                              + self.resp['overview']['provider'] + '\n'
                                              + self.resp['overview']['description'] + '\n')
                if response == {'unrelated_website': True}:
                    return True
                else:
                    self.resp[info].update(response[info])
                pprint(self.resp)

        if url in self.queue:
            for info in self.queue[url]:
                if create_data(soup, contents, info):
                    return

            self.queue.pop(url)

        else:
            for info in info_needed:
                if create_data(soup, contents, info):
                    return
        #==============================================================================#
        
        info_needed = get_info_needed(self.resp)
        print(info_needed)

        new_links = self.get_links(soup)
        pprint(new_links)

        for info in info_needed:
            filtered_links = self.filter_links(new_links, info)

            for link in filtered_links.values():
                link = self.process_link(url, link)

                if link in self.history:
                    pass

                elif link in self.queue:
                    if not info in self.queue[link]:
                        self.queue[link].append(info)

                else:
                    self.queue[link] = [info]
        
        pprint(self.queue)

        while self.queue:
            self.collect_data(list(self.queue.keys())[0])
        
        return

            

Instance = Main()
Instance.collect_data('https://www.nationalhistoryacademy.org/the-academy/rising-10th-12th-grade-students/overview/')