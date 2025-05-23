
from bs4 import BeautifulSoup

filepath = 'llama_client/test_context.html'

from funclib import read_html

html = read_html(filepath)

chtml = BeautifulSoup(html, features="html.parser")

print(chtml.h1) # returns h1
context = chtml.get_text()

