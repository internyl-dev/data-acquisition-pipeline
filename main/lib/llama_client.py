
import requests

filepath = 'llama_client/test_context.html'

def ask_llama(prompt):
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={
            "model": "llama-3.2-3b-instruct",
            "messages": [
                { "role": "user", "content": prompt}
            ],
            "stream": False
        }
        )
    return response
    