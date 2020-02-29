import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from matplotlib import pyplot as plt

with open("./api-key.txt", "r") as keyfile:
    api_key = keyfile.readline().strip()

ts = TimeSeries(key=api_key, output_format="pandas")

symbol = "AAPL"

data, meta_data = ts.get_weekly_adjusted(symbol)
del data["7. dividend amount"]
data = data.sort_index()  # sort to newst date last

source = data["5. adjusted close"]

# EMA
emaPeriod = 13
ema = source.ewm(span=emaPeriod, min_periods=1).mean()
data["ema_"+str(emaPeriod)] = ema

# MACD
macdPeriodFast = 12
macdPeriodSlow = 26
macdPeriodSignal = 9

macd_fast = source.ewm(span=macdPeriodFast, min_periods=1).mean()
macd_slow = source.ewm(span=macdPeriodSlow, min_periods=1).mean()
macd = macd_fast - macd_slow
macd_signal = macd.ewm(span=macdPeriodSignal, min_periods=1).mean()
macd_histo = macd - macd_signal
data["macd"] = macd
data["macd_signal"] = macd_signal
data["macd_histo"] = macd_histo

def elder_impulse(idx):
    if idx == 0:
        return 0

    elder_bulls = (ema.iloc[idx] > ema.iloc[idx-1]) and (macd_histo.iloc[idx] > macd_histo.iloc[idx-1])
    elder_bears = (ema.iloc[idx] < ema.iloc[idx-1]) and (macd_histo.iloc[idx] < macd_histo.iloc[idx-1])
    # red = -1
    # blue = 0
    # green = 1
    elder_color = 1 if elder_bulls else (
        -1 if elder_bears else 0)
    return elder_color


print(data.tail())
print(elder_impulse(-2))
print(elder_impulse(-1))

# figureData = data.iloc[-52:, [4, 7]] # last 52 weeks, close and ema
# figureData.plot(title=str(symbol + " weekly"), grid=True)
# plt.show()
