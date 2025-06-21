
from lib.scrape_html import get_html
import asyncio

url = 'https://www.nyu.edu/admissions/high-school-and-middle-school-programs/high-school-programs/user-experience-design.html'
html = asyncio.run(get_html(url))


from bs4 import BeautifulSoup

soup = BeautifulSoup(html, features="html.parser")
#print(soup)



from lib.truncate_html import truncont
from lib.keywords import *

context = truncont(soup, kw_deadline, 1)
#print(context)



from lib.llama_client import ask_llama
from lib.prompt import llama_requests
import time

start = time.time()

req = llama_requests[0]
print(ask_llama(context + '\n\n' + req).json()['response'])

print(time.time() - start)
