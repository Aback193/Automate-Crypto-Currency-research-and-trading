import scrapy
from scrapy_splash import SplashRequest

DEPTH_LIMIT = 1
RESULTS_LIST = []

# Crawler Class
class CointelegraphSpider(scrapy.Spider):
    name = 'CointelegraphSpider'
    custom_settings = {
        'LOG_ENABLED': True,
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
        #'ROTATING_PROXY_LIST_PATH':'../Lists/proxy_list',
        'SPLASH_URL':'http://0.0.0.0:8050',
        'DUPEFILTER_CLASS':'scrapy_splash.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE':'scrapy_splash.SplashAwareFSCacheStorage'
    }

    # The script clicks pmultiple times to load more content, and extracts entire html.
    script_cointelegraph_click_load_more = """
        function main(splash, args)
            assert(splash:go(args.url))
            assert(splash:wait(5))
            for i = 0,tonumber(args.depth),1
            do 
                input_box = assert(splash:select("a[class=load]"))
                input_box:mouse_click()
                assert(splash:wait(5))
            end
            return {
                html = splash:html(),
                har = splash:har(),
            }
        end """

    splash_args = {
        'wait': 5,
        'depth': DEPTH_LIMIT,
        'lua_source':script_cointelegraph_click_load_more
    }

    # Create search requests.
    def start_requests(self):
        for ticker in self.TICKERS:
            yield SplashRequest('https://cointelegraph.com/search?query={}'.format(ticker), meta={'message':str(ticker)}, callback = self.parse, endpoint='execute', args = self.splash_args) # Cointelegraph JS needed

    # Extract News search resulting links, and go to next page until depth allows it.
    def parse(self, response):
        # Extract clean URLS
        try:
            links = response.xpath("//h2[@class='header']/a/@href").extract()    # Cointelegraph extract links
            for i, url in enumerate(links):
                if url is not None:
                    print("{}.{}".format(i+1, url))
                    yield scrapy.Request(url, callback = self.parse_content, meta={'message':str(response.meta['message'])})
        except Exception as e:
            print(print("Exception {}".format(e)))
            
    def parse_content(self, response):
        global RESULTS_LIST
        try:
            text = [' '.join(line.strip() for line in p.xpath('.//text()').extract() if line.strip()) for p in response.xpath('//p')]
            text_str = ' '.join([str(item) for item in text])
            RESULTS_LIST.append({"Ticker":str(response.meta['message']), "Link":response.url, "Text":text_str})
        except Exception as e:
            print(print("Exception {}".format(e)))
            

# Return crawler results.
def get_CointelegraphSpider():
    return RESULTS_LIST