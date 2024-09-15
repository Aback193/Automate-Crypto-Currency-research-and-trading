# pip install scrapy
# pip install scrapy-fake-useragent             # by default uses huge list of user agetns, with fallback to USER_AGENT
# pip install scrapy-rotating-proxies           # form user:pass@ip:port
import scrapy
from scrapy_splash import SplashRequest

DEPTH_LIMIT = 3
RESULTS_LIST = []


# Crawler Class
class YahooSpider(scrapy.Spider):
    name = "YahooSpider"
    custom_settings = {
        "LOG_ENABLED": False,
        "DEPTH_LIMIT": DEPTH_LIMIT,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_splash.SplashCookiesMiddleware": 723,
            "scrapy_splash.SplashMiddleware": 725,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
            "scrapy_fake_useragent.middleware.RetryUserAgentMiddleware": 401,
            #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
        "SPIDER_MIDDLEWARES": {
            "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
        },
        "DUPEFILTER_CLASS": "scrapy_splash.SplashAwareDupeFilter",
        "FAKEUSERAGENT_PROVIDERS": [
            "scrapy_fake_useragent.providers.FakeUserAgentProvider",  # this is the first provider we'll try
            "scrapy_fake_useragent.providers.FakerProvider",  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent
            "scrapy_fake_useragent.providers.FixedUserAgentProvider",  # fall back to USER_AGENT value
        ],
        "USER_AGENT": "Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "HTTPCACHE_STORAGE": "scrapy_splash.SplashAwareFSCacheStorage",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        #'ROTATING_PROXY_LIST_PATH':'../Lists/proxy_list'
    }

    script_yahoo = """
    function main(splash, args)
        splash:go(args.url)
        assert(splash:wait(2))
        -- accept cookies on yahoo finance
        local scroll_button = splash:select('button[id="scroll-down-btn"]')
        if scroll_button then
            scroll_button:mouse_click()
            assert(splash:wait(1))
        end
        -- bypass consent wall
        local consent_button = splash:select('button[name="agree"]')
        if consent_button then
            consent_button:mouse_click()
            assert(splash:wait(2))
        end
        return {html=splash:html()}
    end"""

    splash_args_script_yahoo = {
        "wait": 2,
        "depth": DEPTH_LIMIT,
        "lua_source": script_yahoo,
    }

    script_yahoo_next_page = """
    function main(splash, args)
        splash:go(args.url)
        assert(splash:wait(2))
        -- bypass consent wall
        local consent_button = splash:select('button[name="agree"]')
        if consent_button then
            consent_button:mouse_click()
            assert(splash:wait(2))
        end
        -- collect search result links
        local results = {}
        results[#results + 1] = splash:html()
        for i = 0,tonumber(args.depth),1
        do
            local next_button = splash:select('a.next')
            if next_button then
                next_button:mouse_click()
                assert(splash:wait(2))
                results[#results + 1] = splash:html()
            end
        end
        return {html=table.concat(results, '')}
    end"""

    splash_args_script_yahoo_next_page = {
        "wait": 2,
        "depth": DEPTH_LIMIT,
        "lua_source": script_yahoo_next_page,
    }

    # Create search requests.
    def start_requests(self):
        for ticker in self.TICKERS:
            yield SplashRequest(
                "https://news.search.yahoo.com/search?p={}&btf={}".format(
                    ticker, self.TIMESPAN_NEWS_SEARCH
                ),
                meta={"message": str(ticker)},
                callback=self.parse,
                endpoint="execute",
                args=self.splash_args_script_yahoo_next_page,
            )

    # Extract News search resulting links, and go to next page until depth allows it.
    def parse(self, response):
        # Extract clean URLS
        links = list(
            set(
                response.xpath(
                    "//div[contains(@class, 'NewsArticle')]/ul/li/h4/a/@href"
                ).extract()
            )
        )
        for url in links:
            if (
                url is not None
                and not str(url).__contains__("cointelegraph.com")
                and not str(url).__contains__("cnyes.com")
                and not str(url).__contains__("beincrypto.com")
                and (str(url).__contains__(".com/") or str(url).__contains__(".net/"))
            ):
                yield SplashRequest(
                    url,
                    meta={"message": str(response.meta["message"])},
                    callback=self.parse_content,
                    endpoint="execute",
                    args=self.splash_args_script_yahoo,
                )

    # Parse discovered links. Extract text from all <p> tags. Website layout independent!
    def parse_content(self, response):
        global RESULTS_LIST
        try:
            text = [
                " ".join(
                    line.strip()
                    for line in p.xpath(".//text()").extract()
                    if line.strip()
                )
                for p in response.xpath(
                    "//body//p[not(ancestor::header) and not(ancestor::footer) and not(ancestor::nav)]"
                )
            ]
            text_str = " ".join([str(item) for item in text])
            if text_str not in RESULTS_LIST and text_str.strip():
                RESULTS_LIST.append(
                    {
                        "Ticker": str(response.meta["message"]),
                        "Link": response.url,
                        "Text": text_str,
                    }
                )
        except Exception as e:
            print(print("Exception {}".format(e)))


# Return crawler results.
def get_YahooSpider():
    return RESULTS_LIST
