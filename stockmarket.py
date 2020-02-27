import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

with open("./api-key.txt", "r") as keyfile:
    api_key = keyfile.readline().strip()

ts = TimeSeries(key=api_key, output_format="pandas")

symbol="amd"

data, meta_data = ts.get_weekly_adjusted(symbol)
data = data.sort_index()

emaPeriod = 20

data["ema_"+str(emaPeriod)] = data["5. adjusted close"].ewm(span=emaPeriod).mean()
print(data.iloc[-5:, [4,7]])
