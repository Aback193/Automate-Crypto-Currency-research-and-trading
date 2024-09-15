import pandas_ta as pta


def rsi(df):
    df_rsi = pta.rsi(df["Close"], length=14)
    """ plt.figure(2)
    plt.title("RSI")
    plt.xlabel('Year')
    plt.ylabel('RSI')
    plt.plot(df_rsi)
    plt.show() """
    return df_rsi


def stoch(df):
    df_stoch = pta.stoch(
        high=df["High"], low=df["Low"], close=df["Close"], k=14, d=3, append=True
    )
    """ plt.figure(3)
    plt.title("STOCH")
    plt.xlabel('Year')
    plt.ylabel('STOCH')
    plt.plot(df_stoch)
    plt.show() """
    return df_stoch["STOCHk_14_3_3"]


def williams(df):
    df_will = pta.willr(high=df["High"], low=df["Low"], close=df["Close"], length=14)
    """ plt.figure(4)
    plt.title("williams")
    plt.xlabel('Year')
    plt.ylabel('williams')
    plt.plot(df_will)
    plt.show()
    print(df_will) """
    return df_will


def macd(df):
    df_macd = pta.macd(close=df["Close"])
    """ plt.figure(5)
    plt.title("MACD")
    plt.xlabel('Year')
    plt.ylabel('MACD')
    plt.plot(df_macd)
    plt.show()
    print(df_macd) """
    return df_macd["MACD_12_26_9"]


def roc(df):
    df_roc = pta.roc(close=df["Close"], length=9)
    """ plt.figure(6)
    plt.title("ROC")
    plt.xlabel('Year')
    plt.ylabel('ROC')
    plt.plot(df_roc)
    plt.show()
    print(df_roc) """
    return df_roc


def obv(df):
    diff = df["Close"].diff()
    df_obv = pta.obv(close=diff, volume=df["Volume"])
    """ plt.figure(6)
    plt.title("OBV")
    plt.xlabel('Year')
    plt.ylabel('OBV')
    plt.plot(df_obv)
    plt.show()
    print(df_obv) """
    return df_obv


def adx(df):
    df_adx = pta.adx(high=df["High"], low=df["Low"], close=df["Close"], length=14)
    """ plt.figure(7)
    plt.title("ADX")
    plt.xlabel('Year')
    plt.ylabel('ADX')
    plt.plot(df_adx)
    plt.show()
    print(df_adx) """
    return df_adx["ADX_14"]


def cmf(df):
    df_cmf = pta.cmf(
        high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"]
    )
    """ plt.figure(8)
    plt.title("CMF")
    plt.xlabel('Year')
    plt.ylabel('CMF')
    plt.plot(df_cmf)
    plt.show()
    print(df_cmf) """
    return df_cmf
