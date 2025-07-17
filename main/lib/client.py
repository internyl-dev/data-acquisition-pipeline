
import requests

def ask_llama(prompt):
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    model = "google/gemma-3n-e2b-it:free"

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

"""from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message)
"""