
from playwright.async_api import async_playwright

async def get_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(url)
        html = await page.evaluate('document.body.innerHTML')
        await browser.close()
    return html



import re

def is_link(s):
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



def keyword_pattern(keyword):
    if keyword.endswith('y'):
        # 'opportunity' -> 'opportunities'
        base = keyword[:-1]
        return fr'\b({base}y|{base}ies)\b'
    elif keyword.endswith(('s', 'x', 'z', 'ch', 'sh')):
        # 'class' -> 'class', 'classes'
        return fr'\b{keyword}(es)?\b'
    else:
        # default: add optional 's'
        return fr'\b{keyword}(s)?\b'



from bs4 import BeautifulSoup

""" truncont contract:
truncont(cont, kw, area)
cont = BeautifulSoup obj
kw   = list
area = int

Returns: 
- str: contains line(s) where keyword(s) in kw appear in cont. 
The string includes area line(s) above and below the line(s) where keyword(s) in kw appear. 
Duplicates of a line are not returned.

Eg.
context = BeautifulSoup('''
<p>line1 content</p>
<p>line2 kw0</p>
<p>line3 content</p>
<p>line4 kw1</p>
<p>line5 content</p>
<p>line6 content</p>
<p>line7 content</p>
<p>line8 kw0</p>
''', features='html.parser')
keywords = ['kw0', 'kw1', 'kw2']

truncont(context, keywords, 1) ->
'''
line1 content
line2 kw0
line3 content
line4 kw1
line5 content
like7 content
line8 kw0

Explanation:
'line6 cont' was left out of the returned value because it was not 1 line above or below any keyword.
"""

def truncont(cont, kw, area):

    # Extracts content from BeautifulSoup object and splits into individual lines
    if isinstance(cont, BeautifulSoup):
        cont = cont.get_text().split('\n')
    else:
        cont = cont.split('\n')
    cont = list(filter(None, cont)) # After splitting, '' may appear. This removes that.

    # Find all lines where keyword in kw appears
    lines = []
    for line in cont:
        for keyword in kw:
            # Non case-sensitive keyword can be followed by 1 s but not any other letter
            if re.search(keyword_pattern(keyword), line, re.I):
                lines.append(line)

    # Use dictionaries to prevent duplicates and maintain order
    indeces = []

    # Find all indeces of lines including those area above and area below
    for line in lines:
        ind = cont.index(line)

        for index in range(ind - area, ind + area + 1):
            indeces.append(index)

    # Get rid of duplicate indeces
    indeces = sorted(set(indeces))
    fincont = []

    for index in indeces:
        try:
            fincont.append(cont[index])
        except IndexError:
            pass
    
    return '\n'.join(fincont)

def find_emails(contents):
    return re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", contents, re.I)

def find_phone_numbers(contents):
    phone_pattern = re.compile(r'''
        # Optional country code: +1, 1, or 1- or 1.
        (?:\+?1[\s.-]?)?

        # Area code: (123), 123, (123)-
        (?:\(?\d{3}\)?[\s.-]?)

        # First 3 digits
        \d{3}

        # Separator
        [\s.-]?

        # Last 4 digits
        \d{4}

        # Optional extension: ext, x, ext., extension followed by digits
        (?:\s*(?:ext\.?|x|extension)\s*\d{2,5})?
        ''', re.VERBOSE | re.I)
    
    return re.findall(phone_pattern, contents)

def find_dates(contents):
    date_pattern = re.compile(r"""
    (?<!\d)                         # Negative lookbehind to avoid matching within a longer number
    (                               # Start capturing group
        (?:\d{1,4})                 # 1-4 digits (year or day or month)
        [./-]                       # separator
        (?:\d{1,2})                 # 1-2 digits
        [./-]                       # separator
        (?:\d{2,4})                 # 2-4 digits (year)
    )
    (?!\d)                          # Negative lookahead to avoid trailing digits
    """, re.VERBOSE | re.I)

    return re.findall(date_pattern, contents)