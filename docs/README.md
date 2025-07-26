# Internyl API Backend

This is the repository for the backend system for the Internyl website. This backend system is responsible for finding the info used by the cards on the internship search page.

Internyl Website Repo: https://github.com/cold-muffin/internyl
<br>
Internyl Website: https://internyl.org

## How to use

### Add API Keys
1. Navigate to `.env` and input any API keys you may have there

### Run main
```
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.venv/scripts/activate

# 3. Install requirements
pip install -r requirements.txt
playwright install

# 4. Run run.py
python run.py
```

## How it Works

### Web Scraping


### HTML Parsing


### Content Summarization


### Client


### Web Crawling


## Tech Used

### Playwright
Used for scraping websites of HTML contents. Capable of loading JavaScript driven websites along with static websites. 

### BeautifulSoup
Used for processing HTML contents scraped from website. Also used in the process of truncating HTML to extract HTML around key information for the AI to use. <br>
Truncating the HTML is important because the AI model has a limited number of usable tokens and also because the size of the HTML content can be very large for certain websites.