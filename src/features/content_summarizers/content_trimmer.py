
import re
import inflect
from bs4 import BeautifulSoup

from .content_keywords import CONTENT_KEYWORDS
from .content_extractors import EmailExtractor, PhoneNumberExtractor, DateExtractor, MoneyExtractor

from src.models import Fields

class ContentTrimmer:
    def __init__(self, content_keywords=CONTENT_KEYWORDS,
                 email_extractor=None, 
                 phone_number_extractor=None,
                 date_extractor=None,
                 money_extractor=None):
        self.content_keywords = content_keywords
        self.p = inflect.engine()

        self.email_extractor = EmailExtractor() or email_extractor
        self.phone_number_extractor = PhoneNumberExtractor or phone_number_extractor
        self.date_extractor = DateExtractor() or date_extractor
        self.money_extractor = MoneyExtractor() or money_extractor

    def _get_plural_regex(self, singular:str) -> str:
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

    def _truncont(self, contents:BeautifulSoup|str, keywords:list, area:int=1) -> str:
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

        # Find all indices of lines where keywords appear
        matching_indices = set()
        
        for i, line in enumerate(contents):
            for keyword in keywords:
                # Non case-sensitive keyword can be followed by 1 s but not any other letter
                if re.search(self._get_plural_regex(keyword), line, re.I):
                    matching_indices.add(i)
                    break  # No need to check other keywords for this line

        # Expand to include surrounding lines (area above and below)
        expanded_indices = set()
        for idx in matching_indices:
            for offset in range(-area, area + 1):
                target_idx = idx + offset
                if 0 <= target_idx < len(contents):  # Ensure index is valid
                    expanded_indices.add(target_idx)

        # Sort indices and extract corresponding lines
        sorted_indices = sorted(expanded_indices)
        fincont = [contents[idx] for idx in sorted_indices]
        
        return '\n'.join(fincont)
    
    def truncate_contents(self, contents:str, required_info:str|Fields, word_limit:int=1500, area:int=1) -> str: # Using word count as a rough estimator for token count
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
        if isinstance(required_info, Fields):
            required_info = required_info.value

        # If the length of the contents is less than the word limit:
        # L> Return the full contents because the model can handle the relatively smaller word count
        # If the required info is overview:
        # L> Return the full contents so that the model can make a general description
        # If the required info is all
        # L> Return the full contents so that the model can use all its information
        if len(contents.split()) < word_limit or required_info == 'overview' or required_info == 'all':
            return contents

        # Truncate for dates as well as keywords if required info is 'dates'
        all_keywords = self.content_keywords[required_info]
        if required_info == 'dates':
            all_keywords.extend(self.date_extractor.extract(contents))
        
        # Truncate for emails and phone numbers as well as keywords if required info is 'contact'
        elif required_info == 'contact':
            all_keywords.extend(self.email_extractor.extract(contents))
            all_keywords.extend(self.phone_number_extractor.extract(contents))

        # Truncate for numbers that have a '$' before them
        elif required_info == 'costs':
            all_keywords.extend(self.money_extractor.extract(contents))

        return self._truncont(contents, all_keywords, area)