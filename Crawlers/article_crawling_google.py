import re
import scrapy
from scrapy_splash import SplashRequest

DEPTH_LIMIT = 2
RESULTS_LIST = []

# Crawler Class
class GoogleSpider(scrapy.Spider):
    name = 'GoogleSpider'
    custom_settings = {
        'LOG_ENABLED': False,
        'DEPTH_LIMIT': DEPTH_LIMIT,
        'DOWNLOADER_MIDDLEWARES':{
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
        'SPIDER_MIDDLEWARES':{
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'FAKEUSERAGENT_PROVIDERS':[
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
            'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
        ],
        'USER_AGENT':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
        #'ROTATING_PROXY_LIST_PATH':'./Lists/proxy_list',
        'SPLASH_URL':'http://0.0.0.0:8050',
        'DUPEFILTER_CLASS':'scrapy_splash.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE':'scrapy_splash.SplashAwareFSCacheStorage'
    }

    # Saves html of each page in array. Page number passed as argument. Returns html array in response
    script_google_next_page = """
    function main(splash, args)
        assert(splash:go(args.url))
        assert(splash:wait(2))
        local result = {}
        for i = 0,tonumber(args.depth),1
        do
            input_box = assert(splash:select("a[id=pnnext]"))
            input_box:mouse_click()
            assert(splash:wait(5))
            result[i] = splash:html()
        end
        return result
    end"""

    splash_args = {
        'wait': 2,
        'depth': DEPTH_LIMIT,
        'lua_source': script_google_next_page
    }

    # Create search requests.
    def start_requests(self):
        for ticker in self.TICKERS:
            yield SplashRequest('https://www.google.com/search?q={}&tbm=nws&source=lnt&tbs=qdr:{}'.format(ticker, self.TIMESPAN_NEWS_SEARCH), meta={'message':str(ticker)}, callback = self.parse, endpoint='execute', args = self.splash_args) # Google JS needed

    # Extract Google search resulting links.
    def parse(self, response):
        links = []
        urls = []
        try:
            [links.append(r) for r in response.xpath("//div/a/@href").extract() if r not in links]      # Google extract links and remove duplicates.
            for url in links:
                if 'https://' in url:
                    res = re.findall(r'(https?://\S+)', url)[0].split('&')[0].rstrip('\\"')
                    if not str(res).__contains__(".google.") and not urls.__contains__(res):
                        urls.append(res)
                        #print(res)
                        yield scrapy.Request(res, callback = self.parse_content, meta={'message':str(response.meta['message'])})
        except Exception as e:
            print(print("Exception {}".format(e)))

    # Parse discovered links. Extract text from all <p> tags. Website layout independent !
    def parse_content(self, response):
        global RESULTS_LIST
        try:
            text = [' '.join(line.strip() for line in p.xpath('.//text()').extract() if line.strip()) for p in response.xpath('//p')]
            text_str = ' '.join([str(item) for item in text])
            RESULTS_LIST.append({"Ticker":str(response.meta['message']), "Link":response.url, "Text":text_str})
        except Exception as e:
            print(print("Exception {}".format(e)))


# Return crawler results.
def get_GoogleSpider():
    return RESULTS_LIST