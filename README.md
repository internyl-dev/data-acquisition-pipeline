# Internyl Data Acquisition via AI Wrapper

This is the repository for the data acquisition pipeline for the Internyl website. This system is responsible for finding the info displayed on the cards of the internship search page.

Internyl Website Repo: https://github.com/internyl-dev/internyl-frontend
<br>
Internyl Website: https://internyl.org

## Table of Contents
1. [How to use](#how-to-use)
  - [Add API Keys](#add-api-keys)
  - [Run main](#run-main)
2. [How it works](#how-it-works)
  - [Web Scraping](#web-scraping)
  - [HTML Parsing](#html-parsing)
  - [Content Summarization](#content-summarization)
  - [Client](#client)
  - [Web Crawling](#web-crawling)
3. [Tech Used](#tech-used)
  - [Playwright](#playwright)
  - [BeautifulSoup](#beautifulsoup)
  - [Firebase](#firebase)
4. [Reflection](#reflection)

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

The entire process is a recursive loop where we take the HTML contents of a webpage, send the HTML to an AI model to extract the target internship information, and find other links from within the webpage that may include any possible missing information. The process then repeats using one of the new links found, adding more data onto the data previously found.

### Web Scraping 

```
src/
└── features/
    └── web_scrapers/
        └── playwright_client.py
```

Given the URL to the homepage of an internship website, we use Playwright to visit the website. Playwright then scrapes the webpage contents. We specifically scrape from the inner body element so as to ignore unneeded script tags.

#### Features
- `scrape_url(url:str) -> str` : The main scraping method. Using Playwright, visit the url and scrape the HTML contents. Returns a string of the HTML contents of the inner body tag.
- `scrape_favicon(url:str) -> str` : Visit a url and scrape the favicon and return the link as a string.

#### Issues + Future Fixes
- **Problem:** The scraper can not yet handle images which is an issue because images can sometimes contain vital information about a program.
- **Solution:** Using Playwright, get the data from the image and have some service extract the text from the image.<br><br>
- **Problem:** The sraper can not yet scrape PDF files. PDF files, though rare, often contain information about programs and are used by some organizations.
- **Solution:** Not top priority, we will revisit and think of a solution soon.<br><br>
- **Problem:** The scraper can not extract data from videos. This issue isn't huge but exists because there are a small amount websites that use videos to communicate vital information.
- **Solution:** No cost effective solution thought of yet. Also not top priority.

### HTML Parsing

```
src/
└── features/
    └── html_cleaners/
        ├── base_html_cleaner.py
        └── html_cleaner.py
```

The HTML contents are first turned into a BeautifulSoup object for parsing. To declutter the HTML, we remove all problematic tags (eg. header, nav footer) to reduce the token count when creating the context. We then remove all unecessary and repeating whitespace to make the context more human-readable.

#### Features
- `clean(soup:BeautifulSoup) -> BeautifulSoup` : The `HTMLDeclutterer` class removes all unecessary HTML elements from the soup object like navs, headers, and form elements, all of which don't provide meaningful data.
- `clean(soup:BeautifulSoup) -> str` : The `HTMLWhitespaceCleaner` class removes all unecessary whitespace and returns a string.

#### Issues + Future Fixes
- **Problem:** One `clean` method returning a `BeautifulSoup` object and the other returning a `str` isn't standard and can cause confusion. 
- **Solution:** Decide between functionality or standardization. I value standardization more since it makes the project more scalable. 

### Content Summarization

```
src/
└── features/
    └── content_summarizers/
        ├── base_content_extractor.py
        ├── content_extractors.py
        ├── content_keywords.py
        └── content_trimmer.py
```

Based on the current state of the dictionary containing all of the info about the program, we determine what info is required. We then truncate the contents for lines that include keywords, including the lines above and below the target lines. <br>
**_NOTE:_** On the first step of the extraction loop, we perform a **bulk extraction** where we don't truncate the HTML contents.

### Client

```
src/
└── features/
    ├── ai_processors/
    │   ├── prompt_chain/
    │   │   ├── executor.py
    │   │   └── prompt_builder.py
    │   ├── prompt_constructors/
    │   │   ├── cpt_builder.py
    │   │   ├── instructions_builder.py
    │   │   ├── instructions.py
    │   │   └── query_builder.py
    │   └── azure_client.py
    └── databases/
        ├── base_database.py
        └── firebase_client.py
```

The client sends a request to the endpoint specified in `.env` and retrieves the response. The prompt is usually based on which required info is being extracted at the moment (except in bulk extraction) The processed schema is then extracted from the response including any other necessary information like the prompt and completions token count for logging purposes. 
<br>**_NOTE:_** In bulk extraction, all required info is requested by the client at once.

### Web Crawling

```
src/
└── features/
    └── web_crawler/
        ├── url_extractor.py
        ├── url_filter.py
        ├── url_keywords.py
        ├── url_processor.py
        └── url_ranker.py
```

If any other info is required, we retrieve all anchor elements from within the scraped HTML and look for valid links. Based on the links and the content of the anchor element, we filter the links, again for specific keywords, to look for links that potentially contain required information. Recursion again starts when we call the entire method with the new link as an argument. <br>
During link extraction, if the queue is detected to have a length higher than a threshold (default 5), we send the queue to the model to intelligently remove any irrelevant links that may have been extracted coincidentally with our keyword system. This system cuts extraction time and costs by a significant amount in websites bloated with irrelevant links. 

## Tech Used

### Playwright
Used for scraping websites of HTML contents. Capable of loading JavaScript driven websites along with static websites. 

### BeautifulSoup
Used for processing HTML contents scraped from website. Also used in the process of truncating HTML to extract HTML around key information for the AI to use. <br>
Truncating the HTML is important because the AI model has a limited number of usable tokens and also because the size of the HTML content can be very large for certain websites.

### Firebase
Used for storing and using the JSON data outputted from this system. 

# Reflection
### !!! Be prepared for a wall of text !!!
#### 8/20/2025
This was the first AI system I've made and implemented in an AI project and thus there were a lot of mistakes that I've made in the development of this project and just as many lessons that I've learned. The mistake that kept haunting me the most throughout the development of this project is the lack of planning or more specifically the failure to realize the importance of a predicted case. When I first thought of the idea for this project, I thought it would be easy, just get the HTML contents of a website, feed it to an AI, and display the output. In essence, that is the project and the simplest case, but I'd soon learn in the middle of development that this was only the ideal. In reality, websites rarely put all of their information in one webpage; it was usually scattered around multiple webpages. Already I had to go back to the drawing board and implement a web crawling system. This is just one example of the hiccups that I went through when making this project, and believe me there were many. Every time I had to go back to drawing new flowcharts the lesson echoes in my head: you should have planned ahead. Inevitably there were a few cases that I probably couldn't have planned ahead but the development of this system would have been a lot faster and smoother if I had better foresight. The great thing about a mistake is that if you take it to heart you learn from it and thus I have the foresight to plan every meticulous detail ahead. <br><br>
There are so many other mistakes and trip-ups that I could talk about but in my opinion the lack of foresight was the biggest and most impactful. Despite my inexperience making large projects like this since this is my first, a lot of things went well but what I'm most proud of is how much I've learned in this project. I'm much more familiar with the python ecosystem and programming standards, especially folder structure which I did not appreciate until now. Despite all that I have learned I still have an immense amount to learn which I will tackle as I continue developing this system and create future projects. <br><br>
This project is in its very, very early stages. I have a lot more plans and ideas for the Internyl website which I can implement once I start collecting data for these programs. The data will be kept in the Firestore and analyzed in the future to add exciting features like date prediction, cost prediction, acceptance rates, and other data which isn't available on the program website. At the time of writing this the Alpha development has started and the website is online but very crudely functional. I will continue to develop and refine this system and learn more about AI and its applications. The future looks exciting not only for the development of Internyl but for the development of AI as an industry.
