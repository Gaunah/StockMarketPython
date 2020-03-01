import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
from matplotlib import pyplot as plt
from datetime import datetime
import os

try:
    with open("./api-key.txt", "r") as keyfile:
        api_key = keyfile.readline().strip()
except FileNotFoundError as e:
    print(e)


symbol = input("Enter stock ticker: ").upper()
date = datetime.now()
filename = "weeklyData_" + symbol + date.strftime("_%Y-%m-%d_%H") + ".zip"

# try to get saved data (if not older than an hour)
oldData = True
try:
    weekly_data = pd.read_pickle("./data/" + filename)
    print("Use {} as datasource.".format(filename))
except FileNotFoundError:
    print("Fetch new data...")
    oldData = False

if not oldData:
    # ts = TimeSeries(key=api_key, output_format="pandas")
    ti = TechIndicators(key=api_key, output_format="pandas")

    # get PriceData
    # weekly_data, meta_data = ts.get_weekly_adjusted(symbol)
    # del weekly_data["7. dividend amount"]
    # weekly_data = weekly_data.sort_index()  # sort to newst date last

    # get MACD
    macd_weekly, macd_meta = ti.get_macd(symbol, interval="weekly",
                                         fastperiod=12, slowperiod=26, signalperiod=9)
    macd_weekly = macd_weekly.sort_index()

    # get EMA
    ema13_weekly, ema13_meta = ti.get_ema(symbol, interval="weekly",
                                          time_period=13)
    ema13_weekly = ema13_weekly.sort_index()

    # join everything
    weekly_data = macd_weekly.join(ema13_weekly)

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
    weekly_data["Elder Impulse"] = [
        colormap[elder_impulse(i)] for i in range(lenght)]

    # save data
    try:
        os.mkdir("./data")
    except FileExistsError:
        pass
    weekly_data.to_pickle("./data/" + filename)

print()
print(weekly_data.tail())
