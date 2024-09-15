from Crawlers import crawler_start
import article_sentiment
import helper_methods

# Coin related variables
TICKERS = ["BTC", "ETH"]
TIMESPAN_NEWS_SEARCH = "w"  # "w" = week, "m" = month

# Crawler related variables
SPIDERS = ["YahooSpider", "CointelegraphSpider", "GoogleSpider"]

if __name__ == "__main__":
    try:
        # Start Crawlers
        crawler_start.run_crawlers(TICKERS, TIMESPAN_NEWS_SEARCH, SPIDERS)

        # Get clean URLs
        cleaned_urls = {
            spider: {
                ticker: crawler_start.get_urls(ticker, spider) for ticker in TICKERS
            }
            for spider in SPIDERS
        }

        # Get articles
        articles = {
            spider: {
                ticker: crawler_start.get_articles(ticker, spider) for ticker in TICKERS
            }
            for spider in SPIDERS
        }

        # Sumarize and calculate sentiment
        summaries = {
            spider: {
                ticker: article_sentiment.summarize(
                    articles[spider][ticker], ticker, spider
                )
                for ticker in TICKERS
            }
            for spider in SPIDERS
        }

        # Sentiment analysis
        sentiment_scores = {
            spider: {
                ticker: article_sentiment.calc_sentiment(summaries[spider][ticker])
                for ticker in TICKERS
            }
            for spider in SPIDERS
        }

        # Calculate total sentiment score
        total_sentiment = helper_methods.total_ticker_sentiment(
            sentiment_scores, TICKERS, SPIDERS
        )
        print("\nTotal snetiment\n{}".format(total_sentiment))

        # Output Sumarization and Sentiment to csv
        sentiment_output = article_sentiment.export_results(
            summaries, sentiment_scores, cleaned_urls, TICKERS, SPIDERS
        )

        sentiment_output.insert(
            0, ["Spider", "Ticker", "Summary", "Sentiment", "Sentiment Score", "URL"]
        )

        helper_methods.create_csv_list("Sentiment.csv", sentiment_output)

        helper_methods.create_xlsx_sentiment_list(
            "Sentiment.xlsx", sentiment_output, total_sentiment, TICKERS, SPIDERS
        )

    except Exception as e:
        print(str(e))
