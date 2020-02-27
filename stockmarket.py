import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

with open("./api-key.txt", "r") as keyfile:
    api_key = keyfile.readline().strip()

ts = TimeSeries(key=api_key, output_format="pandas")

symbol = "AAPL"

data, meta_data = ts.get_weekly_adjusted(symbol)
data = data.sort_index()

source = data["5. adjusted close"]

#EMA
emaPeriod = 13
data["ema_"+str(emaPeriod)] = source.ewm(span=emaPeriod, min_periods=1).mean()

#MACD
macdPeriodFast=12
macdPeriodSlow=26
macdPeriodSignal=9

test = data.iloc[-52:, [4, 7]]
test.plot(title=str(symbol + " weekly"), grid=True)
plt.show()
