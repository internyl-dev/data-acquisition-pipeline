
from src.components import *

from src.lib.guards import Guards
from src.lib.logger import Logger

class Config(WebScraping, HTMLParsing, ContentSummarization, ModelClient, WebCrawling, FirebaseClient, Guards, Logger):
    def __init__(self, log_mode, headless):

        WebScraping.__init__(self, headless=headless)
        HTMLParsing.__init__(self)
        ContentSummarization.__init__(self)
        ModelClient.__init__(self)
        WebCrawling.__init__(self)
        FirebaseClient.__init__(self)
        Guards.__init__(self)
        Logger.__init__(self, log_mode)