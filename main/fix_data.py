import json
"""
input_path = "main/scraped-html-json-responses-medium.jsonl"
output_path = "main/scraped-html-json-responses-medium-cleaned.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        data = json.loads(line)
        for msg in data.get("messages", []):
            if msg.get("role") == "user":

                msg["content"] = msg["content"].split('\n\n\n')[1:]

        outfile.write(json.dumps(data, ensure_ascii=False) + "\n")


input_path = "main/scraped-html-json-responses-medium-cleaned.jsonl"
output_path = "main/scraped-html-json-responses-medium-cleaned0.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        data = json.loads(line)
        for msg in data.get("messages", []):
            if msg.get("role") == "user":

                lst = msg["content"][0].split('\n\n')
                lst.insert(2, 'WEBPAGE CONTENTS START HERE: ')
                msg["content"] = "\n\n".join(lst)

        outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
"""
input_path = "main/scraped-html-json-responses-medium-cleaned.jsonl"
output_path = "main/scraped-html-json-responses-medium-cleaned0.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        data = json.loads(line)
        for msg in data.get("messages", []):
            if msg.get("role") == "user":

                lst = msg["content"][0].split('\n\n')
                lst.insert(2, 'WEBPAGE CONTENTS START HERE: ')
                msg["content"] = "\n\n".join(lst)

        outfile.write(json.dumps(data, ensure_ascii=False) + "\n")