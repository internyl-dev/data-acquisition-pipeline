
import re
from bs4 import BeautifulSoup
from src.components.lib.keywords import keywords

class WebCrawling:
    def __init__(self):
        pass

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
            re.IGNORECASE
        )
        return bool(pattern.match(s))

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
            url = link.get('href')
            text = link.get_text().strip()

            try:
                # Add link to dictionary with the associated text being the key
                # L> For future filtering based off of keywords
                if self.is_link(url):
                    new_links[text] = url

            except Exception: continue

        return new_links

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
            for keyword in keywords['link'][required_info]:

                # If the keyword was found in the text or HREF, add it to the new dictionary
                if re.search(fr'{keyword}', content, re.I) or re.search(fr'{keyword}', links[content], re.I):
                    filtered_links[content] = links[content]
        
        return filtered_links
    
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