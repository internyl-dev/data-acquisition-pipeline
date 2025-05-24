
from bs4 import BeautifulSoup
from funclib import read_html
import re

filepath = 'llama_client/test_context.html'

html = read_html(filepath)
chtml = BeautifulSoup(html, features="html.parser")

#print(chtml.find_all(string = re.compile(r'Stipends', re.I))) # re allows you to ignore case and punctuation

def truncont(cont, s, area):
    cont = cont.get_text().split('\n')
    cont = list(filter(None, cont)) # remove empy strings ''

    s = chtml.find_all(string = re.compile(fr'{s}', re.I))

    ind = cont.index(s[0]) # only for singular cases
    
    return '\n'.join(cont[ind - area : ind + area + 1])


print(truncont(chtml, 'stipends', 1)) # one line above and one line below