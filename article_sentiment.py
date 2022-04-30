# pip install sentencepiece
# pip install transformers
# pip install torch
# pip install pynvml # to check cuda utilization in helper method
import helper_methods

from transformers import pipeline
from transformers import PegasusTokenizer, PegasusForConditionalGeneration

# Sumarization Model setup. Cached inside /home/USER/.cache/huggingface/ on first run. Using CUDA GPU if available, else fallback to CPU.
TORCH_DEVICE = "cuda" if helper_methods.check_cuda() else "cpu"
MODEL_NAME = "human-centered-summarization/financial-summarization-pegasus"
TOKENIZER = PegasusTokenizer.from_pretrained(MODEL_NAME)
MODEL = PegasusForConditionalGeneration.from_pretrained(MODEL_NAME).to(TORCH_DEVICE)

# Summarise all Articles of all tickers
def summarize(articles, ticker, spider):
    print("[{}] Summarizing articles using {} for {}".format(ticker, TORCH_DEVICE.upper(), spider))
    summaries = []
    for article in articles:
        input_ids = TOKENIZER.encode(article, truncation = True, padding = 'longest', max_length = 512, return_tensors = "pt")      # Encode article and return PyTorch tensors, cause Huggingface transformers uses PyTorch. We get number reprezentation of each word 
        output = MODEL.generate(input_ids.to(TORCH_DEVICE), max_length=75, num_beams=5, early_stopping=True)     # Generate model, and specify summary length, and stop when certain level of accuracy is reached. Here again whe generate number ID's
        summary = TOKENIZER.decode(output[0], skip_special_tokens=True)
        summaries.append(summary)
    return summaries

# Calculate sentiment for summarized articles of all tickers. Negative or Positive with confidence score.
def calc_sentiment(summarie):
    sentiment = pipeline("sentiment-analysis")
    sentiment_scores = sentiment(summarie)
    return sentiment_scores

# Export sumarization results to csv
def export_results(summaries, sentiment_scores, cleaned_urls, TICKERS, SPIDERS):
    output = []
    for spider in SPIDERS:
        for ticker in TICKERS:
            for counter in range(len(summaries[spider][ticker])):
                output_this = [
                                spider.partition("Spider")[0],
                                ticker,
                                summaries[spider][ticker][counter],
                                sentiment_scores[spider][ticker][counter]['label'],
                                sentiment_scores[spider][ticker][counter]['score'],
                                cleaned_urls[spider][ticker][counter]
                            ]
                output.append(output_this)
    return output
