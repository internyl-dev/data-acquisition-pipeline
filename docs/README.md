# Backend Testing Site

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