
from src.components import *

from src.lib.guards import Guards
from src.lib.logger import Logger

class Config(WebScraping, HTMLParsing, RequiredInfo, ContentSummarization, ModelClient, WebCrawling, FirebaseClient, SchemaCleanup, Guards, Logger):
    def __init__(self, log_mode, headless):

        WebScraping.__init__(self, headless)
        HTMLParsing.__init__(self)
        RequiredInfo.__init__(self)
        ContentSummarization.__init__(self)
        ModelClient.__init__(self)
        WebCrawling.__init__(self)
        SchemaCleanup.__init__(self)
        FirebaseClient.__init__(self)
        Guards.__init__(self)
        Logger.__init__(self, log_mode)