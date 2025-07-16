
import requests

def ask_llama(prompt):
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    model = "tngtech/deepseek-r1t2-chimera:free"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    json={
        "model": model,
        "messages": [
            { "role": "user", "content": prompt}
        ],
        "stream": False
    }

    response = requests.post(url, headers=headers, json=json)
    return response