# Don't name this file binance.py otherwise strange errors occur!
from binance.client import Client   # pip install python-binance
import datetime
import os

# Binance API key goes here
api = {0: {'api_key' : 'API_KEY', 'api_secret' : 'API_KEY'}}
client = Client(api[0]['api_key'], api[0]['api_secret'])

buy = False
position = "BUY_SELL"   # BUY_SELL = both sell and buy; BUY = just buy; SELL = just sell;
leverage = 100
fee = leverage/10       # binance fee of 10%
gainTreshold = 30       # % gain target to close open position
lossTreshold = -20      # % loss to stop loss open position
gainTotal = 0
winners = 0
losers = 0
subfolderModels = "./BinanceTradeLogs/"

if not os.path.exists(subfolderModels) and subfolderModels != "./":
  # Create a new directory because it does not exist 
  os.makedirs(subfolderModels)

def logFIle(symbol, gain, gainTotal, direction, winners, losers):
    dateTime = datetime.datetime.now()
    file_object = open(subfolderModels+'binance_futures_rf_'+symbol+'_'+position+'logFIle.txt', 'a')
    file_object.write("[ {} ][ {} ]".format(dateTime, direction) + "[ SYMBOL ]: " + symbol + " [ GAIN NO FEE ]: " + str(gain) + " [ TOTAL GAIN ]: " + str(gainTotal) + " [ WIN/LOSS ]: {}/{}".format(winners, losers) + '\n')
    file_object.close()

def getPrice(symbol):
    futures_price = 0
    try:
        futures_price = client.futures_symbol_ticker(symbol=symbol)
        """ print("{} Last price = {}".format((futures_price["symbol"]), futures_price["price"])) """
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
        gain = ((float(currentPrice)/float(buyPrice)) * 100 - 100) * leverage
    elif direction == "SELL":
        gain = ((float(buyPrice)/float(currentPrice)) * 100 - 100) * leverage
    #print("Percentage Gain: {}%".format(gain))
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
    if direction == 'BUY':
        buy = True
        print("\n******************** NEW BUY {} ***********************".format(symbol))
        buyPrice = getPrice(symbol)
        print(buyPrice)
        print("******************** NEW BUY {} ***********************\n".format(symbol))
        while buy:
            if open_close_position(buyPrice, symbol, "BUY"):
                buy = False
                print(symbol + " Total gain: {}% Win/Loss: {}/{}%".format(gainTotal, winners, losers))
    elif direction == 'SELL':
        buy = True
        print("\n******************** NEW SELL {} ***********************".format(symbol))
        buyPrice = getPrice(symbol)
        print(buyPrice)
        print("******************** NEW SELL {} ***********************\n".format(symbol))
        while buy:
            if open_close_position(buyPrice, symbol, "SELL"):
                buy = False
                print(symbol + " Total gain: {}% Win/Loss: {}/{}".format(gainTotal, winners, losers))




