
import re
import json
from bs4 import BeautifulSoup
from ...assets import KEYWORDS

class WebCrawling:
    def __init__(self):
        pass

    @staticmethod
    def is_link(s):
        """
        Finds and returns all links found in a string

        Args:
            contents (str): The text to search links from
        
        Returns:
            value (list): A list of all of the links found within the text
        """
        if '#' in s:
            return False
        
        pattern = re.compile(
            r'^('
            r'https?://[\w.-]+\.[a-zA-Z]{2,}(/[^\s]*)?'  # full URL
            r'|'
            r'//[\w.-]+\.[a-zA-Z]{2,}(/[^\s]*)?'         # scheme-relative
            r'|'
            r'/[^\s]*'                                   # relative path
            r'|'
            r'[\w.-]+\.[a-zA-Z]{2,}(/[^\s]*)?'           # bare domain
            r')$',
        )
        return bool(pattern.match(s))
    
    @staticmethod
    def process_link(url:str, link:str):
        """
        Takes the contents of any HREF assuming that the HREF is an absolute or relative path to a webpage and turns it in an absolute link.

        Args:
            url (str): Absolute webpage URL from which any relative links will be joined with
            link (str): Absolute or relative URL

        Returns:
            value (str): Either the absolute URL result from joining a given absolute URL and relative URL or just the newly given absolute URL.
        """
        if link[0] == '/':
            return '/'.join(url.split('/')[0:3]) + link

        elif link[0:7] == 'http://' or link[0:8] == 'https://':
            return link

        elif link[-1] == '/':
            if not url[-1] == '/':
                url += '/'
            return url + link

    def get_all_links(self, soup:BeautifulSoup):
        """
        Finds all anchor elements from within some HTML contents and returns their content and HREFs if they are valid links.

        Args:
            soup (BeautifulSoup): Contains the HTML contents of the page

        Returns:
            new_links (dict): The contents of anchor elements that have valid links as HREFs 
            with the keys as the content from the original anchor element
        """
        new_links = {}
        links = soup.find_all('a')

        for link in links:
            try:
                # Add link to dictionary with the associated text being the key
                # L> For future filtering based off of keywords
                url = link.get('href').strip()
                text = link.get_text().strip()
                
                if self.is_link(url):
                    new_links[text] = url

            except Exception: 
                continue


        return new_links
    
    def weigh_links_keywords(self, response:dict, all_links:dict):
        weighed_queue = {}

        # Split title based on the delimitters ' ' and '-'
        title_keywords = re.split(' |-', response['overview']['title'])

        matches = 0
        for link in all_links:

            for title_keyword in title_keywords:
                if re.search(fr'{title_keyword}', link, re.I):
                    matches += 1
                if re.search(fr'{title_keyword}', all_links[link], re.I):
                    matches += 1
            
            if not weighed_queue:
                weighed_queue[link] = (all_links[link], matches)
            else:
                for key in weighed_queue:
                    if matches < weighed_queue[key][1]:
                        continue
                    items = list(weighed_queue.items())
                    position = list(weighed_queue.keys()).index(key)
                    items.insert(position, (link, (all_links[link], matches)))
                    weighed_queue = dict(items)
                    break
            
            matches = 0
        
        return weighed_queue

    def weigh_links_url(self, all_links:dict):
        pass

    def filter_links(self, links:dict, required_info:str):
        """
        Filters all anchor elements based on their content and URL with keywords corresponding to the required info.

        Args:
            links (dict): The contents of anchor elements that have valid links as HREFs with the keys as the content from the original anchor element
            required_info (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)

        Returns:
            filtered_links (dict): Only the links that contain the relevant keywords in either their content or url
        """
        filtered_links = {}
        for content in links:
            for keyword in KEYWORDS['link'][required_info]:

                # If the keyword was found in the text or HREF, add it to the new dictionary
                if re.search(fr'{keyword}', content, re.I) or re.search(fr'{keyword}', links[content], re.I):
                    filtered_links[content] = links[content]
        
        return filtered_links
        
    def web_crawling_main(self, raw_html:str, url:str):
        # ... Obtained new required information

        # Get all links from within the raw HTML
        all_links = self.get_all_links(BeautifulSoup(raw_html, features='html.parser'))
        self.logger.debug(f'All links:\n{json.dumps(all_links)}')

        for required_info in self.all_required_info:
            filtered_links = self.filter_links(all_links, required_info)

            for link in filtered_links.values():
                link = self.process_link(url, link)

                # Skip links we've already visited
                if link in self.history:
                    continue

                # If link is in queue: add info if it was not already there
                elif link in self.queue:
                    if required_info not in self.queue[link]:
                        self.queue[link].append(required_info)

                # Link is not in history or queue: add it into the queue
                else:
                    self.queue[link] = [required_info]

        # Send the excessively large queue to the model
        # to remove unecessary links
        if len(self.queue) >= 5:
            self.logger.debug(f"Excessively large queue size detected: sending request to model...")
            self.model_eval_links()

        # Recursing ...