import alpaca_trade_api as tradeapi
import json, os
import datetime

with open('keys.json') as keysfile:
	keys = json.load(keysfile)

os.environ['APCA_API_BASE_URL'] = keys['Alpaca_Endpoint']
os.environ['APCA_API_KEY_ID'] = keys['Alpaca_API_Key']
os.environ['APCA_API_SECRET_KEY'] = keys['Alpaca_Secret_Key']


api = tradeapi.REST()

# Get daily price data for AAPL over the last 5 trading days.
from wallstreet import Stock, Call, Put

s = Stock('AAPL')
print(s.price)

"""
# Check if AAPL is tradable on the Alpaca platform.
barset = api.get_barset('AAPL', 'minute', limit=1)

print(barset)
"""