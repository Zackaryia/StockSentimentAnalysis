import alpaca_trade_api as tradeapi
import portfolio_manager
import json

with open('keys.json') as keysfile:
	keys = json.load(keysfile)

api = tradeapi.REST(keys['Alpaca_API_Key'], keys['Alpaca_Secret_Key'], keys['Alpaca_Endpoint'])

PortfolioManager_instance = portfolio_manager.PortfolioManager(api=api)

# Check if the market is open now.
clock = api.get_clock()
print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

def check_markets_open():
	return clock.is_open

def redistribute(stocks_and_points):

	PortfolioManager_instance.add_items(stocks_and_points)
	PortfolioManager_instance.percent_rebalance('timeout')
	