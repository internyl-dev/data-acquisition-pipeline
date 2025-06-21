
import requests

filepath = 'llama_client/test_context.html'

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
    