
from fastapi import FastAPI
import requests
import time

filepath = 'llama_client/test_context.html'

app = FastAPI()

from funclib import read_html

context = (read_html(filepath))
#from truncate_html import context

def ask_llama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        )
    return response
    


from prompt import llama_requests

start = time.time()

for req in llama_requests:
    response = (ask_llama(context + '\n\n' + req))
    print(response.json()['response'])


print(time.time() - start)
