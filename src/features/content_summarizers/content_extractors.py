
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
    
class MoneyExtractor(ContentExtractor):
    def extract(self, s:str):
        """
        Finds and returns all monetary amounts found in a string

        Args:
            s (str): The text to search monetary amounts from
        
        Returns:
            value (list): A list of all monetary amounts found within the text
        """
        money_pattern = re.compile(r"""
        (                           # Start capturing group (moved to capture symbol too)
            (?:                     # Non-capturing group for currency symbol prefix
                (?:USD|EUR|GBP|CAD|AUD|JPY|CNY|INR)  # Currency codes
                \s*                 # Optional whitespace
            )?
            (?:                     # Currency symbols
                [\$£€¥₹]            # Common currency symbols
            )?
            \s*                     # Optional whitespace
            \b                      # Word boundary
            (?:
                \d{1,3}(?:,\d{3})+(?:\.\d{2})?  # Numbers with commas: 1,000 or 1,000.00
                |                   # OR
                \d+(?:\.\d{2})?     # Numbers without commas: 100 or 100.00
            )
            \b                      # Word boundary
            \s*                     # Optional whitespace
            (?:                     # Non-capturing group for currency suffix
                (?:USD|EUR|GBP|CAD|AUD|JPY|CNY|INR|dollars?|euros?|pounds?|yen)
            )?
        )                           # End capturing group
        """, re.VERBOSE | re.I)

        return re.findall(money_pattern, s)
    
if __name__ == "__main__":
    test_text = """Ladder Internships is a world-class internship program for ambitious students. In the program, students work with top start-ups and NGOs to develop real-world projects. The Startup internship program runs 8 weeks, costs $2990, and involves weekly meetings with a supervisor from the start-up. The CEO internship program: costs $4990 and involves working directly with a start-up CEO from a FAANG background (Facebook, Google, etc.). This is our program for our most ambitious interns. The Combination program: Offers our flagship CEO internship program in combination with a mentored research program. The joint program is $7400. There is full financial aid for students with need. The program is selective. The admission deadline for the Winter cohort (starting December 8th) is November 16th."""
    
    extractor = MoneyExtractor()
    results = extractor.extract(test_text)
    
    print("Money amounts found:")
    print(results)