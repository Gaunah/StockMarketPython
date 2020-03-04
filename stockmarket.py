import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
from matplotlib import pyplot as plt
from datetime import datetime
import os

workingDir = os.path.dirname(__file__)
dataPath = workingDir + "/data/"

try:
    with open(workingDir+"/api-key.txt", "r") as keyfile:
        api_key = keyfile.readline().strip()
except FileNotFoundError as e:
    print(e)


symbol = input("Enter stock ticker: ").upper()
date = datetime.now()
filename = "weeklyData_" + symbol + date.strftime("_%Y-%m-%d_%H") + ".zip"

# try to get saved data (if not older than an hour)
oldData = True
try:
    weekly_data = pd.read_pickle(dataPath + filename)
    print("Use {} as datasource.".format(filename))
except FileNotFoundError:
    print("Fetch new data...")
    oldData = False

if not oldData:
    ts = TimeSeries(key=api_key, output_format="pandas")
    ti = TechIndicators(key=api_key, output_format="pandas")

    # get PriceData
    weekly_price, price_meta = ts.get_weekly_adjusted(symbol)
    del weekly_price["7. dividend amount"]
    weekly_price = weekly_price.sort_index()  # sort to newst date last

    # get MACD
    macd_weekly, macd_meta = ti.get_macd(symbol, interval="weekly",
                                         fastperiod=12, slowperiod=26, signalperiod=9)
    macd_weekly = macd_weekly.sort_index()

    # get EMA
    ema13_weekly, ema13_meta = ti.get_ema(symbol, interval="weekly",
                                          time_period=13)
    ema13_weekly = ema13_weekly.sort_index()

    # join everything
    weekly_data = weekly_price.join(macd_weekly.join(ema13_weekly))

    def elder_impulse(idx):
        if idx == 0:
            return 0

        emaCur = weekly_data["EMA"].iat[idx]
        emaLast = weekly_data["EMA"].iat[idx-1]
        mhCur = weekly_data["MACD_Hist"].iat[idx]
        mhLast = weekly_data["MACD_Hist"].iat[idx-1]

        elder_bulls = (emaCur > emaLast) and (mhCur > mhLast)
        elder_bears = (emaCur < emaLast) and (mhCur < mhLast)
        # red = -1
        # blue = 0
        # green = 1
        elder_color = 1 if elder_bulls else (
            -1 if elder_bears else 0)
        return elder_color

    colormap = {-1: "red", 0: "blue", 1: "green"}
    # add Elder Impulse
    lenght = len(weekly_data.index)
    print("Calc elder impulse...")
    weekly_data["Elder Impulse"] = [elder_impulse(i) for i in range(lenght)]

    # save data
    try:
        os.mkdir(dataPath)
    except FileExistsError:
        pass
    weekly_data.to_pickle(dataPath + filename)

print()
print(weekly_data.tail())

elderNow = weekly_data["Elder Impulse"].iat[-1]
elderLast = weekly_data["Elder Impulse"].iat[-2]
signal = "buy signal" if elderNow > elderLast else (
    "sell signal" if elderNow < elderLast else "neutral")
print(signal)
