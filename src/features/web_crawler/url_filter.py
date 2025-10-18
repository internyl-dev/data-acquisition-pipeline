
import re

from .url_keywords import LINK_KEYWORDS
from src.models import Fields

class URLFilter:
    def filter(self, urls:dict, target_info:str|Fields):
        """
        Filters all anchor elements based on their content and URL with keywords corresponding to the required info.

        Args:
            links (dict): The contents of anchor elements that have valid links as HREFs with the keys as the content from the original anchor element
            required_info (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)

        Returns:
            href[urls] (dict): Only the links that contain the relevant keywords in either their content or url
        """
        if isinstance(target_info, Fields):
            target_info = target_info.value
            
        filtered_links = {}
        for href in urls:
            for keyword in LINK_KEYWORDS[target_info]:

                # If the keyword was found in the text or HREF, add it to the new dictionary
                if re.search(fr'{keyword}', href, re.I) or re.search(fr'{keyword}', urls[href], re.I):
                    filtered_links[href] = urls[href]
        
        return filtered_links

if __name__ == "__main__":
    urls = {
        "https://example.com/apply": "Apply Now",
        "https://example.com/fees": "Tuition and Fees",
        "https://example.com/about": "About Us",
        "https://example.com/contact": "Contact Information"
    }
    url_filter = URLFilter()
    print(url_filter.filter(urls, "costs"))