
from bs4 import BeautifulSoup
from funclib import read_html
import re

filepath = 'llama_client/test_context.html'

html = read_html(filepath)
soup = BeautifulSoup(html, features="html.parser")

soup = BeautifulSoup('''
<p>line-2 content</p>
<p>line-1 content</p>
<p>line0 content</p>  
<p>line1 content</p>
<p>line2 kw0</p>
<p>line3 content</p>
<p>line4 kw1</p>
<p>line5 content</p>
<p>line6 content</p>
<p>line7 content</p>
<p>line8 kw0</p>
<p>line9 content</p>
<p>line10 content</p>
<p>line11 content</p>                    
''', features="html.parser")

"""
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
    cont = cont.get_text().split('\n')
    cont = list(filter(None, cont)) # After splitting, '' may appear. This removes that.

    # Find all lines where keyword in kw appears
    lines = []
    for line in cont:
        for keyword in kw:
            if bool(re.search(re.compile(fr'{keyword}', re.I), line)):
                lines.append(line)

    # Use dictionaries to prevent duplicates and maintain order
    fincont = {}

    # Find all 
    for line in lines:
        ind = cont.index(line)

        for li in cont[ind - area : ind + 1]:
            fincont[li] = ''
        
        fincont[cont[ind]] = ''

        for li in cont[ind : ind + area + 1]:
            fincont[li] = ''
    
    return '\n'.join(fincont.keys())


print(truncont(soup, ['kw0', 'kw1', 'kw2'], 1)) # one line above and one line below