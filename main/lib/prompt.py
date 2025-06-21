
llama_requests = ["""
You are a helpful assistant helping me with extracting information from a website.
Extract the deadline for the program in the following format:
Make sure to include the MM (month), DD (day), and YY (year)

"deadline": {
  "date": [MM-DD-YY],
  "time": [if a specific time is given, format as HH:MM AM/PM.  
            If only a general time of day is mentioned (e.g., "Noon", "Midnight"), include that.  
            If no time is mentioned at all, return an empty string ""]
}
                  
DO NOT WRITE CODE, FIND THE VALUES YOURSELF AND RETURN THEM
                  
Return in the format of the following examples:
"deadline": {
  "date": 09-21-25,
  "time": 12:00 AM
}    
"deadline": {
  "date": 01-29-26,
  "time": Midnight
}           
""",



"""
You are a helpful assistant helping me with extracting information from a website.
Extract the start and end dates of the program.

DO NOT WRITE CODE, FIND THE VALUES YOURSELF AND RETURN THEM

Return in the format:
"date": {
  "start": [MM-DD-YY],
  "end": [MM-DD-YY]
}
""",



"""
You are a helpful assistant helping me with extracting information from a website.
Extract the eligibility information in terms of school years only.

Use "freshman", "sophomore", "junior", or "senior" (9th = freshman, 10th = sophomore, 11th = junior, 12th = senior)
If the text mentions “Rising”, or "Rising to" (not case sensitive), make "rising" true

DO NOT WRITE CODE, FIND THE VALUES YOURSELF AND RETURN THEM

Return using the format of the following examples: (keep the exact format, including quotation marks)
"eligibility": {
    "rising": true,
    "grade": ["Freshman", "Sophomore", "Junior", "Senior"]
    }
If rising is mentioned
"eligibility": {
    "rising": true,
    "grade": ["Rising Sophomore", "Rising Junior"]
    }
""",



"""
You are a helpful assistant helping me with extracting information from a website.
Extract the primary subject or field of the program.
Return only the subject (e.g., "Computer Science", "Biology", "Engineering").
Do not include extra description or unrelated topics.

Return in the format:
"subject": string

DO NOT WRITE CODE, FIND THE VALUES YOURSELF AND RETURN THEM

Return in the format of the following examples:
"subject": "Computer Science"
"subject": "Biology"
"subject": "Engineering"
""",



"""
You are a helpful assistant helping me with extracting information from a website.
Extract the cost of the program using the following rules:

If it says "stipend" and gives a number then return "Stipend $amount"
If it says "stipend" but no amount is given then return "Stipend Available"
If a dollar amount is given and it’s not free then return that number as an integer

Return in the following format:
"cost": integer or string

DO NOT WRITE CODE, FIND THE VALUES YOURSELF AND RETURN THEM
"""
]

llama_request = """
Given the contents of the HTML file, extract and return the information in the exact structure shown below.
Do not add any new keys. Only fill in the existing fields. Return only the JSON object.
{
  "title": [title of the program],

  "deadline": {
    "date": [format: MM-DD-YY],
    "time": [if a specific time is given, format as HH:MM AM/PM. If only a general time of day is mentioned (e.g., "noon", "midnight"), include that. If no time is mentioned, use an empty string ""]
  },

  "date": {
    "start": [format: MM-DD-YY],
    "end": [format: MM-DD-YY]
  },

  "eligibility": [
    [List the eligible school years: freshman, sophomore, junior, or senior. Add "Rising" before a year if specified (e.g., "Rising Junior")]
  ],

  "field": [Only the primary subject or field, e.g., "Computer Science"],

  "cost": [
    If it says "stipend" and gives a number, return: "Stipend $amount".
    If it says "stipend" but no amount is given, return: "Stipend Available".
    If it's free or $0, return: "free".
    If a dollar amount is given (not free), return that amount as an integer (e.g., 1500).
    If none of the above is specified, return -1.
  ]
}
"""