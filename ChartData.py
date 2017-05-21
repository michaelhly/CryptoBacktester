from urllib.parse import urlencode
import json
import time
import requests
import hmac,hashlib
from urllib.parse import urlencode

class ChartDataLoader:

    def __init__(self, currencyPair, start, end, period):

        url = ('https://poloniex.com/public?command=returnChartData' +
            '&currencyPair=%s&start=%s&end=%s&period=%s' %
            (currencyPair,start,end,period))
        try:
            ret = requests.get(url)
            print(ret)
        except:
            print("Failed to fetch chart data")
            print(ret)

        rawData = json.loads(ret.text)

        self._date = []
        self._high = []
        self._low = []
        self._open = []
        self._close = []
        self._volume = []
        self._quoteVolume = []
        self._weightedAverage = []

        for item in rawData:
            self._date.append(item["date"])
            self._high.append(item["high"])
            self._low.append(item["low"])
            self._open.append(item["open"])
            self._close.append(float(item["close"]))
            self._volume.append(item["volume"])
            self._quoteVolume.append(item["quoteVolume"])
            self._weightedAverage.append(item["weightedAverage"])

    def getDates(self):
        date = self._date
        return date

    def getHigh(self):
        high = self._high
        return high

    def getLow(self):
        low = self._low
        return low

    def getOpen(self):
        p_open = self._open
        return p_open

    def getClose(self):
        close = self._close
        return close

    def getVolume(self):
        volume = self._volume
        return volume

    def getQuoteVolume(self):
        qVolume = self._quoteVolume
        return qVolume

    def getWeightedAverage(self):
        wAverage = self._quoteVolume
        return wAverage
