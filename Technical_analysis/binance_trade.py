# Don't name this file binance.py otherwise strange errors occur!
import os
import datetime
from binance.client import Client  # pip install python-binance

# Binance API key
client = Client(os.environ["API_KEY"], os.environ["API_SECRET"])

buy = False
position = "BUY_SELL"  # BUY_SELL = both sell and buy; BUY = just buy; SELL = just sell;
leverage = 100
fee = leverage / 10  # binance fee of 10%
gainTreshold = 120  # % gain target to close open position
lossTreshold = -60  # % loss to stop loss open position
gainTotal = 0
winners = 0
losers = 0
subfolderModels = "./BinanceTradeLogs/"

if not os.path.exists(subfolderModels) and subfolderModels != "./":
    # Create a new directory if not exist
    os.makedirs(subfolderModels)


def logFIle(symbol, gain, gainTotal, direction, winners, losers):
    dateTime = datetime.datetime.now()
    file_object = open(
        subfolderModels
        + "binance_futures_rf_"
        + symbol
        + "_"
        + position
        + "logFIle.txt",
        "a",
    )
    file_object.write(
        "[ {} ][ {} ]".format(dateTime, direction)
        + "[ SYMBOL ]: "
        + symbol
        + " [ GAIN NO FEE ]: "
        + str(gain)
        + " [ TOTAL GAIN ]: "
        + str(gainTotal)
        + " [ WIN/LOSS ]: {}/{}".format(winners, losers)
        + "\n"
    )
    file_object.close()


def getPrice(symbol):
    futures_price = 0
    try:
        futures_price = client.futures_symbol_ticker(symbol=symbol)
    except Exception as e:
        print(e)
    return futures_price["price"]


def open_close_position(buyPrice, symbol, direction):
    global gainTotal
    global leverage
    global gainTreshold
    global lossTreshold
    global winners
    global losers
    currentPrice = getPrice(symbol)
    while currentPrice == 0:
        currentPrice = getPrice(symbol)
    if direction == "BUY":
        gain = ((float(currentPrice) / float(buyPrice)) * 100 - 100) * leverage
    elif direction == "SELL":
        gain = ((float(buyPrice) / float(currentPrice)) * 100 - 100) * leverage
    if gain >= gainTreshold:
        winners += 1
        gainTotal = gainTotal + gain - fee
        logFIle(symbol, gain, gainTotal, direction, winners, losers)
        print("\nPosition sold for " + str(gainTreshold) + "% gain")
        return True
    elif gain <= lossTreshold:
        losers += 1
        gainTotal = gainTotal + gain - fee
        logFIle(symbol, gain, gainTotal, direction, winners, losers)
        print("\nPosition sold for " + str(lossTreshold) + "% loss")
        return True
    return False


# SELL # BUY
def init(direction, symbol):
    global buy
    global gainTotal
    global winners
    global losers
    if direction == "BUY":
        buy = True
        print(
            "\n******************** NEW BUY {} ***********************".format(symbol)
        )
        buyPrice = getPrice(symbol)
        print(buyPrice)
        print(
            "******************** NEW BUY {} ***********************\n".format(symbol)
        )
        while buy:
            if open_close_position(buyPrice, symbol, "BUY"):
                buy = False
                print(
                    symbol
                    + " Total gain: {}% Win/Loss: {}/{}%".format(
                        gainTotal, winners, losers
                    )
                )
    elif direction == "SELL":
        buy = True
        print(
            "\n******************** NEW SELL {} ***********************".format(symbol)
        )
        buyPrice = getPrice(symbol)
        print(buyPrice)
        print(
            "******************** NEW SELL {} ***********************\n".format(symbol)
        )
        while buy:
            if open_close_position(buyPrice, symbol, "SELL"):
                buy = False
                print(
                    symbol
                    + " Total gain: {}% Win/Loss: {}/{}".format(
                        gainTotal, winners, losers
                    )
                )
