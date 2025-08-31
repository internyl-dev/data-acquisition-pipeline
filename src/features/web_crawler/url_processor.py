
import re

class URLProcessor:
    @staticmethod
    def is_url(s:str):
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
    def process_url(base_url:str, url:str):
        """
        Takes the contents of any HREF assuming that the HREF is an absolute or relative path to a webpage and turns it in an absolute link.

        Args:
            url (str): Absolute webpage URL from which any relative links will be joined with
            link (str): Absolute or relative URL

        Returns:
            value (str): Either the absolute URL result from joining a given absolute URL and relative URL or just the newly given absolute URL.
        """
        if url[0] == '/':
            return '/'.join(base_url.split('/')[0:3]) + url

        elif url[0:7] == 'http://' or url[0:8] == 'https://':
            return url

        elif url[-1] == '/':
            if not base_url[-1] == '/':
                base_url += '/'
            return base_url + url