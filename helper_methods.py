# pip install openpyxl
import os
import subprocess as sp
import re
import torch.cuda as cuda
from openpyxl import Workbook
import csv

# List to .csv
def create_csv_list(file_name, output_data):
    with open(file_name, mode="w", newline="") as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(output_data)

# Data Frame to .csv
def create_csv_df(file_name, df):
    df.to_csv(file_name, encoding='utf-8', index=False)

# List to .xlsx file with multiple sheets
def create_xlsx_sentiment_list(file_name, output_data, total, TICKERS, SPIDERS):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Sentiment"
    for item in output_data:
        ws1.append(item)
    top_row = ["Spider", "Ticker", "Positive ratio %", "Total sentiment"]
    ws2 = wb.create_sheet(title="Total sentiment")
    ws2.append(top_row)
    for spider in SPIDERS:
        for ticker in TICKERS:
            tmp = [spider, ticker, total[spider][ticker]["Positive ratio %"], total[spider][ticker]["Total sentiment"]]
            ws2.append(tmp)
    wb.save(filename = file_name)
    wb.close()

# Calculate positive sentiment ratio in %
def total_ticker_sentiment(sentiment_scores, TICKERS, SPIDERS):
    total_sentiment = {}
    for spider in SPIDERS:
        ticker_sentiment = {}
        for ticker in TICKERS:
            sentiments = [sentiment_scores[spider][ticker][i]["label"] for i in range(sentiment_scores[spider][ticker].__len__())]
            if sentiments.count("NEGATIVE") > 0:
                positive_ratio = round((sentiments.count("POSITIVE")/sentiments.count("NEGATIVE")), 2)
            else:
                positive_ratio = sentiments.count("POSITIVE")
            final_sentiment = "NEUTRAL"
            if positive_ratio > 1:
                final_sentiment = "POSITIVE"
            elif positive_ratio < 1:
                final_sentiment = "NEGATIVE"
            ticker_sentiment[ticker] = {"Total sentiment":final_sentiment, "Positive ratio %":positive_ratio}
        total_sentiment[spider] = ticker_sentiment
    return total_sentiment

# Check if CUDA device is available. Must go with try, because it throws exception when GPU is busy.
def check_cuda():
    try:
        if cuda.is_available():
            if cuda.utilization() < 10:
                cuda_mem_used = sp.Popen("nvidia-smi --query-gpu=memory.used --format=csv | grep ' MiB' | cut -d ' ' -f1", shell=True, stdout=sp.PIPE).stdout.read().decode('utf-8')
                cuda_mem_total = sp.Popen("nvidia-smi --query-gpu=memory.total --format=csv | grep ' MiB' | cut -d ' ' -f1", shell=True, stdout=sp.PIPE).stdout.read().decode('utf-8')
                cuda_mem = int(int(cuda_mem_used)/int(cuda_mem_total)*100)
                if cuda_mem < 10:
                    print("=>>> CUDA device {} detected, and ready for use! <<<=".format(cuda.get_device_name()))
                    return True
                else:
                    kill_cuda_processes()
                    return False
            else:
                print("=>>> CUDA device busy, using only CPU! <<<=")
                return False
        else:
            print("=>>> CUDA device not available, using CPU only! <<<=")
            return False
    except Exception as e:
        print(("=>>> CUDA device not available, using CPU only! <<<=\n{}".format(str(e))))
        return False

# Kill hanging CUDA processes, after unexpected shutdown
def kill_cuda_processes():
    try:
        print("\n=>>> CUDA device processes killed, please restart app.py! <<<=\n")
        os.system("fuser -k /dev/nvidia* >/dev/null 2>&1")
    except Exception as e:
        print(str(e))