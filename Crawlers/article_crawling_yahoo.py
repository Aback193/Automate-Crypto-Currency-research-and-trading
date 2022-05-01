# pip install scrapy
# pip install scrapy-fake-useragent             # by default uses huge list of user agetns, with fallback to USER_AGENT
# pip install scrapy-rotating-proxies           # form user:pass@ip:port
import scrapy

DEPTH_LIMIT = 4
RESULTS_LIST = []

# Crawler Class
class YahooSpider(scrapy.Spider):
    name = 'YahooSpider'
    custom_settings = {
        'LOG_ENABLED': False,
        'DEPTH_LIMIT': DEPTH_LIMIT,
        'DOWNLOADER_MIDDLEWARES':{
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
            #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
        'FAKEUSERAGENT_PROVIDERS':[
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
            'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
        ],
        'USER_AGENT':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
        #'ROTATING_PROXY_LIST_PATH':'../Lists/proxy_list'
    }

    # Create search requests.
    def start_requests(self):
        for ticker in self.TICKERS:
            yield scrapy.Request('https://news.search.yahoo.com/search?p={}&btf={}'.format(ticker, self.TIMESPAN_NEWS_SEARCH), meta={'message':str(ticker)}, callback = self.parse)

    # Extract News search resulting links, and go to next page until depth allows it.
    def parse(self, response):
        # Extract clean URLS
        links = response.xpath("//div[contains(@class, 'NewsArticle')]/ul/li/h4/a/@href").extract()
        for url in links:
            if url is not None and not str(url).__contains__("cointelegraph.com") and not str(url).__contains__("cnyes.com") and(str(url).__contains__(".com/") or str(url).__contains__(".net/")):
                yield scrapy.Request(url, callback = self.parse_content, meta={'message':str(response.meta['message'])})

        # Go to next page
        next_page_url = response.xpath("//a[contains(@class, 'next')]/@href").extract()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url[0], callback = self.parse, meta={'message':str(response.meta['message'])})
            
    # Parse discovered links. Extract text from all <p> tags. Website layout independent!
    def parse_content(self, response):
        global RESULTS_LIST
        try:
            text = [' '.join(line.strip() for line in p.xpath('.//text()').extract() if line.strip()) for p in response.xpath('//p')]
            text_str = ' '.join([str(item) for item in text])
            #print(response.url)
            RESULTS_LIST.append({"Ticker":str(response.meta['message']), "Link":response.url, "Text":text_str})
        except Exception as e:
            print(print("Exception {}".format(e)))


# Return crawler results.
def get_YahooSpider():
    return RESULTS_LIST
