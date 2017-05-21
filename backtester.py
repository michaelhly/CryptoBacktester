import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from ChartData import ChartDataLoader
import talib

CURRENCY     = 'BTC'
ASSET        = 'ETH'
PAIR         = ('%s_%s'%(CURRENCY, ASSET))
CANDLE       = [300, 900, 1800, 7200, 14400, 86400]
INTERVAL     = CANDLE[0]
PERIOD       = 1000 #How many candles
END          = 9999999999 #9999999999 is to current; else unix


# INITIALIZED STORAGE VALUES
storage = {}
storage['trades'] = 0

# STARTING PORTFOLIO
portfolio = {}
portfolio['assets'] = 0
portfolio['currency'] = 1

# INFO OBJECTS
info = {}
info['begin'] = int(time.time())-PERIOD*INTERVAL
info['index'] = 0
info['interval'] = INTERVAL
info['current_time'] = info['begin']
info['end']=info['begin']+PERIOD*INTERVAL
SATOSHI = 0.00000001
ANTISAT = 100000000.0

#LOAD ChartData
try:
    chartdata = ChartDataLoader(PAIR, info['begin'], END, INTERVAL)
except:
    print("Failed to fetch chart data")

dates = chartdata.getDates()
close_prices = chartdata.getClose()
volume = chartdata.getVolume()

### ------ Uncomment Data You Would Need ------###
#high = chartdata.getHigh()
#low = chartdata.getLow()
#open_prices = chartdata.getOpen()
#quoted_volume = chartdata.getQuoteVolume()
#weighted_average = getWeightedAverage()

#CHART VARS
fig = plt.figure()
ax1 = plt.subplot2grid((5,4),(0,0),rowspan = 4, colspan = 4, axisbg='darkslategray')
ax2 = plt.subplot2grid((5,4),(4,0), sharex = ax1, rowspan = 1, colspan = 4)

#HELPER METHODS (from litepresence)
def holdings(initial_price):

    # STORE STARTING PORTFOLIO
    storage['begin_max_assets']=(
        portfolio['currency']/(initial_price)+portfolio['assets'])
    storage['begin_max_currency']=(
        portfolio['currency']+portfolio['assets']*(initial_price))
    storage['start_price'] = initial_price

def test_sell(time, price):

        portfolio['currency'] = portfolio['assets']*price
        print ('[%s] %s SELL %.2f %s at %s sat value %.2f %s' % (time,
            storage['trades'], portfolio['assets'], ASSET, price/SATOSHI,
            portfolio['currency'], CURRENCY))
        portfolio['assets'] = 0
        ax1.plot(time,price,markersize=8,
            marker='o',color='coral',label='sell')

def test_buy(time, price):

        portfolio['assets'] = portfolio['currency']/(price)
        print ('[%s] %s BUY %.2f %s at %s sat value %.2f %s' % (time,
            storage['trades'], portfolio['assets'], ASSET, price/SATOSHI,
            portfolio['currency'], CURRENCY))
        portfolio['currency'] = 0
        ax1.plot(time,price,markersize=8,
            marker='o',color='lime',label='buy')


#INITIALIZE INITAL HOLDINGS
holdings(close_prices[0])

#INITIALIZE SRATEGY OBJECTS TO KEEP TRACK OF
upperband = []
middleband = []
lowerband = []
BBANDcontext = []
timeframe = 50


# MAIN LOOP

def main():
    # INDEX: Index of current candle from the historical data, start from 0 to len(dates)
    # DATE:  Date of the current candle
    for index,date in enumerate(dates):

        #--------------------------------IMPLEMENT STRATEGY HERE--------------------------------------------#

        #Bollinger Band strategy from http://pythontrader.blogspot.com/2015/05/ta-lib-usage-bollinger-bands.html
        close = close_prices[index]
        BBANDcontext.append(close)

        #Set up Bollinger Bands
        if index >= timeframe:
            if(index > timeframe):
                BBANDcontext.pop(0)

            context = np.array(BBANDcontext)
            upper, middle, lower = talib.BBANDS(context,timeframe,nbdevup=2,nbdevdn=2,matype=0)
            upperband.append(upper[-1:])
            middleband.append(middle[-1:])
            lowerband.append(lower[-1:])


            # If price is below the recent lower band and we have
            # no long positions then invest the entire
            #portfolio value into ASSET
            if close < lower[-1:]:
                if portfolio['currency'] > 0:
                    test_buy(time = date, price=close)
                    storage['trades']+=1

             # If price is above the recent upper band and we have
             # no short positions then invest the entire
             # portfolio value to short ASSET
            elif close > upper[-1:]:
                if portfolio['assets'] > 0:
                    test_sell(time = date, price=close)
                    storage['trades']+=1



def chart():
    # PLOT OBJECTS
    ax1.plot(dates[timeframe:],close_prices[timeframe:],linestyle="",marker='.',
        color='white',label='PRICE')
    ax1.plot(dates[timeframe:],upperband,color='b',label='UPPERBAND')
    ax1.plot(dates[timeframe:],middleband,color='g',label='MIDDLEBAND')
    ax1.plot(dates[timeframe:],lowerband,color='r',label='LOWERBAND')

    # PLOT VOLUME
    ax2.bar(dates[timeframe:],volume[timeframe:], width=200)


    #FORMATTING
    plt.suptitle("BACKTEST RESULT: %s, %s - %s" % (PAIR, datetime.datetime.utcfromtimestamp(info['begin']), datetime.datetime.utcfromtimestamp(info['end'])))
    plt.setp(ax1.get_xticklabels(), visible = False)
    ax1.autoscale(enable=True, axis='y')
    ax1.autoscale(enable=True, axis='x')
    ax1.get_xaxis().get_major_formatter().set_useOffset(False)
    ax1.get_xaxis().get_major_formatter().set_scientific(False)
    ax1.grid(True)

    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(90)


#ENDING SUMMARY (from litepresence)
def summary():

    # MOVE TO CURRENCY
    if portfolio['assets'] > 0:
        print('stop() EXIT TO CURRENCY')
        test_sell(info['end'], price = close_prices[-1])
    # CALCULATE RETURN ON INVESTMENT
    end_max_assets=(
        portfolio['currency']/(close_prices[-1])+portfolio['assets'])
    end_max_currency=(
        portfolio['currency']+portfolio['assets']*(close_prices[-1]))
    roi_assets = end_max_assets/storage['begin_max_assets']
    roi_currency = end_max_currency/storage['begin_max_currency']
    # FINAL REPORT
    print('===============================================================')
    print('START DATE........: %s' % time.ctime(info['begin']))
    print('END DATE..........: %s' % time.ctime(info['end']))
    print('START PRICE.......: %s satoshi' % ANTISAT*int(storage['start_price']))
    print('END PRICE.........: %s satoshi' % ANTISAT*int(close_prices[-1]))
    print('START MAX ASSET...: %.2f %s' % (storage['begin_max_assets'],ASSET))
    print('END MAX ASSET.....: %.2f %s' % (end_max_assets,ASSET))
    print('ROI ASSET.........: %.1fX' % roi_assets)
    print('START MAX CURRENCY: %.2f %s' % (storage['begin_max_currency'],CURRENCY))
    print('END MAX CURRENCY..: %.2f %s' % (end_max_currency, CURRENCY))
    print('ROI CURRENCY......: %.1fX' % roi_currency)
    print('===============================================================')
    print('~===END BACKTEST=========================~')




main()
chart()
summary()

plt.show()
