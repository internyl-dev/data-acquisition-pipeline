
import re

from .url_keywords import LINK_KEYWORDS

class URLFilter:
    def filter(self, urls:dict, required_info:str):
        """
        Filters all anchor elements based on their content and URL with keywords corresponding to the required info.

        Args:
            links (dict): The contents of anchor elements that have valid links as HREFs with the keys as the content from the original anchor element
            required_info (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)

        Returns:
            href[urls] (dict): Only the links that contain the relevant keywords in either their content or url
        """
        filtered_links = {}
        for href in urls:
            for keyword in LINK_KEYWORDS[required_info]:

                # If the keyword was found in the text or HREF, add it to the new dictionary
                if re.search(fr'{keyword}', href, re.I) or re.search(fr'{keyword}', urls[href], re.I):
                    filtered_links[href] = urls[href]
        
        return filtered_links
        