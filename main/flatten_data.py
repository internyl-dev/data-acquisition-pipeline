import json

input_path = "main/scraped-html-json-responses-small.jsonl"
output_path = "main/scraped-html-json-responses-small-flattened.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        data = json.loads(line)
        for msg in data.get("messages", []):
            if msg.get("role") == "assistant" and isinstance(msg.get("content"), dict):
                # Flatten the dictionary to a string using json.dumps
                msg["content"] = json.dumps(msg["content"], ensure_ascii=False)
        outfile.write(json.dumps(data, ensure_ascii=False) + "\n")