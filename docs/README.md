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

The entire process is a recursive loop where we take the HTML contents of a webpage, send the HTML to an AI model to extract our target internship information, and find other links from within the webpage that may include any possible missing information. The process recurses from one of the links found in the aforementioned last step.

### Web Scraping 
#### `src/components/web_scraping.py`

Given the URL to the homepage of an internship website, we use Playwright to visit the website. Playwright then scrapes the inner body element so as to ignore unneeded script tags. 

### HTML Parsing
#### `src/components/html_parsing.py`

The HTML contents are first turned into a BeautifulSoup object for parsing. To declutter the HTML, we remove all problematic tags (eg. header, nav footer) to reduce the token count when creating the context. We then remove all unecessary and repeating whitespace to make the context more human-readable.

### Content Summarization
#### `src/components/content_summ.py`

Based on the current state of the dictionary containing all of the info about the program, we determine what info is required. We then truncate the contents for lines that include keywords (found in `src/components/lib/keywords.py`), including the lines above and below the target lines. <br>
**_NOTE:_** On the first step of the extraction loop, we perform a **bulk extraction** where we don't truncate the HTML contents.

### Client
#### `src/components/client.py`



### Web Crawling
#### `src/components/web_crawling.py`

## Tech Used

### Playwright
Used for scraping websites of HTML contents. Capable of loading JavaScript driven websites along with static websites. 

### BeautifulSoup
Used for processing HTML contents scraped from website. Also used in the process of truncating HTML to extract HTML around key information for the AI to use. <br>
Truncating the HTML is important because the AI model has a limited number of usable tokens and also because the size of the HTML content can be very large for certain websites.