# Backend Testing Site

# How to use

### Add API Keys
1. Navigate to `src/.env` and input any API keys there

### Run main
```
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.venv/scripts/activate

# 3. Install requirements
pip install -r requirements.txt`

# 4. Run the main file
python src/main.py
```

# also everything below this is false and will be updated in the next commit

## Tech Used

### FastAPI
Responsible for all API calls. 

### Playwright
Used for scraping websites of HTML contents. Capable of loading JavaScript driven webssites along with static websites. Cross browser compatible and cross language compatible but Python is used for this project.

### BeautifulSoup
Used for processing HTML contents scraped from website. Also used in the process of truncating HTML to extract HTML around key information for the AI to use. <br>
Truncating the HTML is important because the AI model has a limited number of usable tokens and also because the size of the HTML content can be very large for certain websites.

## AI

### Ollama
Llama3.2 was chosen because it is open source and powerful despite it's relatively low size. <br>
Llama3.2 still has to undergo fine tuning because its outputs aren't consistent and in this specific use case I've noticed it straying from instructions no matter if it was given in chunks or all at once. I plan on using Unsloth to fine tune this model.