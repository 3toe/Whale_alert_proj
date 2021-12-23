import requests
import datetime 
import calendar
import numpy
import pandas

# generate unix timestamp for transactions start date
# get current time
timestamp = datetime.datetime.utcnow()
# time (in seconds) we want to look back for transactions (max for free account is 3600)
lookback = 3600
utc_timestart = calendar.timegm(timestamp.utctimetuple()) - lookback

# i will get the cursor from each request.get, and i need to pass that into each 
# subsequent request to get the next chunk of data 

# make API call using these variables as the full URL to request:
baseURL = 'https://api.whale-alert.io/v1/transactions?api_key='
# look into requests library for ways to sneak API key in as a cleaner object while hiding the actual key.
min_val = '&min_value=500000'
starttime = '&start=' + str(utc_timestart)
cursor = None

# make initial request with null cursor to get first cursor and throw that into the while loop below:
# while cursor is not None, make a request with a new cursor, and update the cursor to the next one (add 6 second wait while using free account):

response = requests.get(baseURL + '1P1rAEuChUXXCm2XYhxtArAqy2GmBhp7' + min_val + starttime)
# print error code
print(response)

# generate graph's time axis and empty data list
timeAxis = []
i = 0
for i in range(lookback):
   timeAxis.append(utc_timestart + i)

# need to generate [timeIndex], which will be a 1D array with equal size to timeAxis, and contains the same data, converted
# from unix time code to human-readable time.  This will be the row labels for my dataframe.
timeIndex = timeAxis

# Something in this loop converts my UTC to datetime...:
for e in range(0, 3600, 1):
   timeIndex[e] = datetime.datetime.strftime(datetime.datetime.fromtimestamp(timeAxis[e]), "%m-%d-%Y %H:%M:%S")

# ...So I have to repeat this block:
timeAxis = []
i = 0
for i in range(lookback):
   timeAxis.append(utc_timestart + i)

# placeholder 0's for the data
dataempty = [0] * lookback
# stack timestamp and data arrays
DFtemplate = numpy.transpose(numpy.stack([timeAxis,dataempty]))
# create the dataframe object
dft = pandas.DataFrame(DFtemplate, [timeIndex], ['TS', 'Amt_USD'])

# print(dft)

# SymsSoFar = ['btc', 'xrp', 'trx', 'busd', 'usdt', 'eth', 'gusd']

# initialize our lists for each currency
btcamt = []
btcts = []
xrpamt = []
xrpts = []
usdtamt = []
usdtts = []
ethamt = []
ethts = []
busdamt = []
busdts = []

# fill lists from API call
for data in response.json()['transactions']:
   if data['symbol'] == 'btc':
      btcamt.append(data['amount_usd'])
      btcts.append(data['timestamp'])
   if data['symbol'] == 'xrp':
      xrpamt.append(data['amount_usd'])
      xrpts.append(data['timestamp'])
   if data['symbol'] == 'usdt':
      usdtamt.append(data['amount_usd'])
      usdtts.append(data['timestamp'])
   if data['symbol'] == 'eth':
      ethamt.append(data['amount_usd'])
      ethts.append(data['timestamp'])
   if data['symbol'] == 'busd':
      busdamt.append(data['amount_usd'])
      busdts.append(data['timestamp'])

# print(btcts[:5])

btcStack = numpy.transpose(numpy.stack([btcts,btcamt])).astype(int)

btcdf = pandas.DataFrame(btcStack, ['row']*len(btcamt), ['TS', 'Amt_USD'])

print(dft)
print(btcdf)

# so far, this merges the dataframes into nothing:
btcMerged = pandas.merge(dft, btcdf)
print(btcMerged)

"""
   # this will give me 3 lists of all the request data I care about, but it's not ordered:
   for data in response.json()['transactions']:      
   sym.append(data['symbol'])
   amt.append(data['amount_usd'])
   ts.append(data['timestamp']) 
"""