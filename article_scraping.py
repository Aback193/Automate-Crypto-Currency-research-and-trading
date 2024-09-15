# pip install bs4
import re
import requests
from bs4 import BeautifulSoup

EXCLUDE_URL = ["accounts", "maps", "support", "global"]  # For google search.


def search_engine_search_ticker_links(ticker, TIMESPAN_NEWS_SEARCH):
    # Search for Stock News using Google search engine and Yahoo Finance
    # Request all information from URL, and parse it using BeautifulSoup, to find all links
    print("[{}] Searching for news".format(ticker))
    search_url = "https://www.google.com/search?q=yahoo+finance+{}&tbm=nws&source=lnt&tbs=qdr:{}".format(
        ticker, TIMESPAN_NEWS_SEARCH
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }
    request = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(request.text, "html.parser")
    atags = soup.find_all("a")  # grab all links from search result
    hrefs = [link["href"] for link in atags]
    return hrefs


def url_strip(URLs, ticker):
    # Strip out unwanted URLs
    print("[{}] Cleaning URLs".format(ticker))
    val = []
    for url in URLs:
        if "https://" in url and not any(exc in url for exc in EXCLUDE_URL):
            res = re.findall(r"(https?://\S+)", url)[0].split("&")[0]
            val.append(res)
    return list(set(val))


def get_articles(URLs, ticker):
    # Search and Scrape Cleaned URLs
    print("[{}] Scraping news articles".format(ticker))
    articles = []
    for url in URLs:
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "html.parser")
        results = soup.find_all("p")
        text = [res.text for res in results]
        words = " ".join(text).split(" ")
        article = " ".join(words)
        articles.append(article)
    return articles
