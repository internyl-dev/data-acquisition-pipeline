
import re
import inflect
from bs4 import BeautifulSoup

from .content_keywords import CONTENT_KEYWORDS

class ContentTrimmer:
    def __init__(self, content_keywords=CONTENT_KEYWORDS):
        self.content_keywords = content_keywords
        self.p = inflect.engine()

    def _get_plural_regex(self, singular:str):
        """
        Takes a word and turns it into its plural form

        Args:
            word (str): Single word to turn plural
        
        Returns:
            value (str): Regex pattern to match the singular and plural word
        """
        plural = self.p.plural(singular)

        singular_escaped = re.escape(singular)
        plural_escaped = re.escape(plural)

        pattern = rf'\b({singular_escaped}|{plural_escaped})\b'

        return pattern

    
    def _truncont(self, contents:BeautifulSoup|str, keywords:list, area:int=1):
        """
        Truncates any string separated by new lines and returns some amount of lines 
        above and below lines containing keywords in either the singular or plural form.

        Args:
            contents (str): Contains the contents of the webpage
            keywords (list): A list of keywords to match
            area (int, optional): The amount of lines above and below lines containing the keyword

        Returns:
            value (str): Truncated contents of the webpage
        """
        # Extracts content from BeautifulSoup object and splits into individual lines
        if isinstance(contents, BeautifulSoup):
            contents = contents.get_text().split('\n')
        else:
            contents = contents.split('\n')
        contents = list(filter(None, contents)) # After splitting, '' may appear. This removes that.

        # Find all lines where keyword in kw appears
        lines = []
        for line in contents:
            for keyword in keywords:
                # Non case-sensitive keyword can be followed by 1 s but not any other letter
                if re.search(self._get_plural_regex(keyword), line, re.I):
                    lines.append(line)

        # Use dictionaries to prevent duplicates and maintain order
        indeces = []

        # Find all indeces of lines including those area above and area below
        for line in lines:
            ind = contents.index(line)

            for index in range(ind - area, ind + area + 1):
                indeces.append(index)

        # Get rid of duplicate indeces
        indeces = sorted(set(indeces))
        fincont = []

        for index in indeces:
            try:
                fincont.append(contents[index])
            except IndexError:
                pass
        
        return '\n'.join(fincont)
    
    def truncate_contents(self, contents:str, required_info:str, word_limit:int=1500, area:int=1): # Using word count as a rough estimator for token count
        """
        Truncates any string separated by new lines 
        and returns only the lines near to and containing keywords based off of the info required.

        Args:
            contents (str): Contains the contents of the webpage
            info_required (str): Any valid required info section (overview, eligibility, dates, locations, costs, contact)
            word_limit (int, optional): Automatically set to 1500, the word limit for the string to start truncating

        Returns:
            value (str): Truncated contents of the webpage
        """

        # If the length of the contents is less than the word limit:
        # L> Return the full contents because the model can handle the relatively smaller word count
        # If the required info is overview:
        # L> Return the full contents if the required info is 'overview so that the model can make a general description
        if len(contents.split()) < word_limit or required_info == 'overview':
            return contents

        # Truncate for dates as well as keywords if required info is 'dates'
        if required_info == 'dates':
            all_keywords = (self.content_keywords[required_info] 
                        + self.find_dates(contents))
        
        # Truncate for emails and phone numbers as well as keywords if required info is 'contact'
        elif required_info == 'contact':
            all_keywords = (self.content_keywords[required_info] 
                        + self.find_emails(contents) 
                        + self.find_phone_numbers(contents))
            
        # Don't truncate contents if we're performing a bulk extraction
        elif required_info == 'all':
            return contents
            
        # Or simply truncate for keywords associated with the required info
        else:
            all_keywords = self.content_keywords[required_info]

        return self._truncont(contents, all_keywords, area)