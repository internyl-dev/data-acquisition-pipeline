
import re

from .base_content_extractor import ContentExtractor

class EmailExtractor(ContentExtractor):
    def extract(self, s:str):
        """
        Finds and returns all emails found in a string

        Args:
            contents (str): The text to search emails from
        
        Returns:
            value (list): A list of all of the emails found within the text
        """
        return re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", s, re.I)

class PhoneNumberExtractor(ContentExtractor):
    def extract(self, s:str):
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
    
        return re.findall(phone_pattern, s)

class DateExtractor(ContentExtractor):
    def extract(self, s:str):
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

        return re.findall(date_pattern, s)