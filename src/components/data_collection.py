
import json
import time

class DataCollection:
    def __init__(self):
        self.DATA_FILE_PATH = 'main/scraped-html-json-responses.jsonl'
        self.data = {"messages": [{"role": "user","content": ""},{"role": "assistant","content": {}}]}

    def read_last_jsonl(self):
        """
        Reads last line in a JSONL file using byte reading.

        Returns:
            value (dict): The parsed JSON content
        """
        with open(self.DATA_FILE_PATH, "rb") as f:
            f.seek(0, 2)  # Go to end of file
            pos = f.tell() - 1

            while pos > 0:
                f.seek(pos)
                char = f.read(1)
                if char == b"\n":
                    # Read the next line after newline
                    last_line = f.readline().decode("utf-8").strip()
                    if last_line != '':
                        return json.loads(last_line)
                pos -= 1

            # If we reach start of file, read from beginning (in case single line no newline)
            f.seek(0)
            last_line = f.readline().decode("utf-8").strip()
            return json.loads(last_line)

    def save_to_jsonl(self, context:str):
        """
        Dumps the prompt and context into the JSONL file 
        and waits until the user has inputted content in the form of the ideal model response.

        Args:
            context (str): The prompt and context to give to the model
        
        Returns:
            value (dict): The user-inputted ideal response
        """
        data = self.data.copy()
        data['messages'][0]['content'] = context

        with open(self.DATA_FILE_PATH, "a+", encoding="utf-8") as file:
            file.write(json.dumps(self.data) + "\n")
            file.flush()

            loops = 0

            c = self.read_last_jsonl()
            while not c['messages'][1]['content']:
                loops += 1
                time.sleep(1)
                c = self.read_last_jsonl()
                print('Read last line', loops, 'time(s)')
        
        return self.read_last_jsonl()['messages'][1]['content']
    
    def create_data(self, context:str, required_info:str):
        """
        Dumps the data JSON schema with context into JSONL file, waits for user input, and reads the response.

        Args:
            context (str): 

        Returns:
            value (bool): Returns True if the response is "{'unrelated_website': True}"
        """
        response = self.save_to_jsonl(context)
        
        if response == {'unrelated_website': True}:
            return True
            
        self.response[required_info].update(response[required_info])