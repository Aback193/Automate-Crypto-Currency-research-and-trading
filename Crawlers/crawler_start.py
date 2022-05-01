# pip install scrapy
# pip install scrapy-fake-useragent             # by default uses huge list of user agetns, with fallback to USER_AGENT
# pip install scrapy-rotating-proxies           # form user:pass@ip:port
# Run Splash ==> docker run -p 8050:8050 scrapinghub/splash --max-timeout 3600 <==. Splash docker image is automatically downloaded if not detected.
from . import article_crawling_yahoo as YahooSpider
from . import article_crawling_cointelegraph as CointelegraphSpider
from . import article_crawling_google as GoogleSpider

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings

CRAWLER_RESULTS = {}

# Run crawlers and retrieve results from each of them into dictionary.
def run_crawlers(TICKERS, TIMESPAN_NEWS_SEARCH, SPIDERS):
    # Start all defined crawlers. CrawlerRunner is much better choice, because it can run multiple crawlers, while CrawlerProcess can not!
    print("=>>> Crawlers gathering articles... <<<=")
    s = get_project_settings()
    s.update({
        "LOG_ENABLED": "False"
    })
    runner = CrawlerRunner(s)
    @defer.inlineCallbacks
    def crawl():
        for spider in SPIDERS:
            yield runner.crawl(getattr(eval(spider), str(spider)), TICKERS=TICKERS, TIMESPAN_NEWS_SEARCH=TIMESPAN_NEWS_SEARCH)
        reactor.stop()
    crawl()
    reactor.run()
    
    # Get results of all crawlers.
    for spider in SPIDERS:
        CRAWLER_RESULTS[spider] = getattr(eval(spider), "get_" + str(spider))()


# Retrieve clean URLS per Ticker and Spider.
def get_urls(ticker, spider):
    urls = []
    if CRAWLER_RESULTS.__contains__(spider):
        for i, key in enumerate(CRAWLER_RESULTS[spider]):
            if CRAWLER_RESULTS[spider][i]["Ticker"] == ticker:
                urls.append(CRAWLER_RESULTS[spider][i]["Link"])
    return urls

# Retrieve Articles per Ticker and Spider.
def get_articles(ticker, spider):
    articles = []
    counter = 0
    if CRAWLER_RESULTS.__contains__(spider):
        for i, key in enumerate(CRAWLER_RESULTS[spider]):
            if CRAWLER_RESULTS[spider][i]["Ticker"] == ticker:
                counter += 1
                articles.append(CRAWLER_RESULTS[spider][i]["Text"])
                #print("\n{}. {} Ticker: {} Link: {} Text: {}".format(counter, spider, CRAWLER_RESULTS[spider][i]["Ticker"], CRAWLER_RESULTS[spider][i]["Link"], CRAWLER_RESULTS[spider][i]["Text"][:500]))
    return articles
