
import re
from bs4 import BeautifulSoup
from components.lib.keywords import keywords

class ContentSummarization:
    def __init__(self):
        pass

    @staticmethod
    def pluralize(word:str):
        """
        Takes a word and turns it into its plural form

        Args:
            word (str): Single word to turn plural
        
        Returns:
            value (str): Plural version of the word
        """
        if word.endswith('y'):
            # 'opportunity' -> 'opportunities'
            base = word[:-1]
            return fr'\b({base}y|{base}ies)\b'
        elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
            # 'class' -> 'classes'
            return fr'\b{word}(es)?\b'
        else:
            # default: 's'
            return fr'\b{word}(s)?\b'

    @staticmethod
    def find_emails(contents:str):
        """
        Finds and returns all emails found in a string

        Args:
            contents (str): The text to search emails from
        
        Returns:
            value (list): A list of all of the emails found within the text
        """
        return re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", contents, re.I)

    @staticmethod
    def find_phone_numbers(contents:str):
        """
        Finds and returns all phone numbers found in a string

        Args:
            contents (str): The text to search phone numbers from
        
        Returns:
            value (list): A list of all of the phone numbers found within the text
        """
        phone_pattern = re.compile(r'''
                                   
            (?:\+?1[\s.-]?)?         # Optional country code: +1, 1, or 1- or 1.
            (?:\(?\d{3}\)?[\s.-]?)   # Area code: (123), 123, (123)-
            \d{3}                    # First 3 digits
            [\s.-]?                  # Separator
            \d{4}                    # Last 4 digits

            # Optional extension: ext, x, ext., extension followed by digits
            (?:\s*(?:ext\.?|x|extension)\s*\d{2,5})? 
                                   
            ''', re.VERBOSE | re.I)
        
        return re.findall(phone_pattern, contents)

    @staticmethod
    def find_dates(contents:str):
        """
        Finds and returns all dates found in a string

        Args:
            contents (str): The text to search dates from
        
        Returns:
            value (list): A list of all of the dates found within the text
        """
        date_pattern = re.compile(r"""
        (?<!\d)                     # Negative lookbehind to avoid matching within a longer number
        (                           # Start capturing group
            (?:\d{1,4})             # 1-4 digits (year or day or month)
            [./-]                   # separator
            (?:\d{1,2})             # 1-2 digits
            [./-]                   # separator
            (?:\d{2,4})             # 2-4 digits (year)
        )
        (?!\d)                      # Negative lookahead to avoid trailing digits
        """, re.VERBOSE | re.I)

        return re.findall(date_pattern, contents)
    
    def truncont(self, contents:BeautifulSoup|str, keywords:list, area:int=1):
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
                if re.search(self.pluralize(keyword), line, re.I):
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
            all_keywords = (keywords[required_info] 
                        + self.find_dates(contents))
        
        # Truncate for emails and phone numbers as well as keywords if required info is 'contact'
        elif required_info == 'contact':
            all_keywords = (keywords[required_info] 
                        + self.find_emails(contents) 
                        + self.find_phone_numbers(contents))
            
        # Or simply truncate for keywords associated with the required info
        else:
            all_keywords = keywords[required_info]

        return self.truncont(contents, all_keywords, area)