import tweepy
import json
import datetime
import time
import AlpacaInterface

#Sentiment Analyzer

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()


# Importing Keys

with open('keys.json') as keysfile:
	keys = json.load(keysfile)


#adding support for sentiment analysis of multiple stoinks

Tickers = ['$GME', '$RKT', '$UWMC', '$PLTR', '$SKT', '$AMC', '$TSLA', '$SPY', '$APPL', "$BB", '$NIO', '$PLC', '$MFGP']
Total = {
	"total_sentiment": 0.0,
	"Stocks_analized": 0
}

Stocks_template = {}
for ticker in Tickers:
	Stocks_template[ticker] = {"total_sentiment": 0.0, "Stocks_analized": 0}
	
Stocks = Stocks_template.copy()

Tweets_analyzed = []

# Setting up Tweepy (Twitter API Wrapper for python)

auth = tweepy.OAuthHandler(keys['API_Key'], keys['API_Secret_Key'])
auth.set_access_token(keys['Access_Token'], keys['Access_Token_Secret'])

api = tweepy.API(auth)


# Getting the text of a status, including retweets.

def get_status_full_text(status):
	if 'extended_tweet' in status.__dict__.keys():
		return status.extended_tweet['full_text'] # extended text
	elif 'retweeted_status' in status.__dict__.keys():
		if "full_text" in status.retweeted_status.__dict__.keys():
			return status.retweeted_status.full_text #retweet full text
		else:
			if status.retweeted_status.truncated:
				return status.retweeted_status.extended_tweet['full_text'] # Retweet extended text full text
			else:
				return status.text #retweet normal text
	else:
		return status.text

"""import threading
import os

def a():
    os.system('python3 servejson.py')

threads = []
threads.append(threading.Thread(target=a))
threads[-1].setDaemon(True)
threads[-1].start() # Runs to serve json file to html
"""

Sentiment_Debug_Info = False

class MyStreamListener(tweepy.StreamListener):

	def on_status(self, status):
		Start_time_of_analysis = time.time() 
		text = get_status_full_text(status)
		if Sentiment_Debug_Info: 
			print("##########################")
			print(text)
			print("## SENTAMINT ##")

		##ADD TWEET TO Tweets_analyzed ##
		Tweets_analyzed.append(status.id_str)#f"https://twitter.com/{status.user.screen_name}/status/{status.id_str}")
		## ##

		sentiment = analyzer.polarity_scores(text) #create custom popularity score if 🚀 set compound == 0.7

		global Stocks
		global Total

		Total["Stocks_analized"] += 1
		Total["total_sentiment"] += sentiment['compound']

		words = [word.lower() for word in text.split(' ')]

		for Stock_ticker in Tickers:
			if Stock_ticker.lower() in words:
				Stocks[Stock_ticker]["Stocks_analized"] += 1
				Stocks[Stock_ticker]["total_sentiment"] += sentiment['compound']

		if Sentiment_Debug_Info:
			print(f"Tweet's Sentiment:          {sentiment}")
			print(f"Amount of tweets analyzed:  {Total['Stocks_analized']}")
			print(f"Sum of all tweet sentiment: {Total['total_sentiment']}")

		End_time_of_analysis = time.time() 

		if Sentiment_Debug_Info:
			print(f"Time to analyze in milli  : {(End_time_of_analysis-Start_time_of_analysis) * 1000.0}")
			
			print("##########################")


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener, tweet_mode="extended")
myStream.filter(track=Tickers, is_async=True)

last_6_stock_trends = []

Special_Data = [f"STARTED ON {time.time()}"]

last_10_minute_action = time.time()

while True:
	time.sleep(5)

	#Writing data for future visualizeation 
	with open('Stocks_Sentiment.json', 'w+') as json_file:
		json_file.write(json.dumps({"stocks": Stocks, "other_info": {"AllStocks": Total, "Last6Stocks": last_6_stock_trends, "Time": time.time(), "Last10minAction": last_10_minute_action, "Other": Special_Data, "Tweets": Tweets_analyzed}}, indent = 1))
		Tweets_analyzed = []

	# Checks to update the stock 
	if time.time() - last_10_minute_action >= 60*1:
		
		Special_Data.append(f"10 min event {time.time()}")
		
		last_10_minute_action = time.time()

		if len(last_6_stock_trends) >= 10: # Creates a snapshot of the sentiment of the stocks every 10 minutes
			last_6_stock_trends.pop(0)

		last_6_stock_trends.append(Stocks.copy())

		Stocks = Stocks_template.copy() # Resets currecnt snapshot to set up the next snapshot

	
		# Then allocates funds according to the Snapshots every time a snapshot is taken
		if AlpacaInterface.check_markets_open(): 
			Special_Data.append(f"MAKING A ALPACA STOCK THING AT {time.time()}")
			Avged_Snapshot = Stocks_template.copy()

			for snapshot in last_6_stock_trends:
				for ticker in snapshot.keys():
					Avged_Snapshot[ticker]['total_sentiment'] += snapshot[ticker]['total_sentiment']
					Avged_Snapshot[ticker]['Stocks_analized'] += snapshot[ticker]['Stocks_analized']

			# Now that the past 6 snapshots have been sumed, I will average them and pakcage them for the AlpacaInterface program.
			
			# First remove any stocks with negative sentiment and get the total sentiment of the positive stocks
			total_sentiment_of_positive_stocks = 0
			To_be_popped_stock_tickers = []
			for Stock_Ticker in Avged_Snapshot.keys():
				if Avged_Snapshot[Stock_Ticker]['total_sentiment'] < 0:
					To_be_popped_stock_tickers.append(Stock_Ticker)
				else:
					total_sentiment_of_positive_stocks += Avged_Snapshot[Stock_Ticker]['total_sentiment']
			
			for Stock_Ticker in To_be_popped_stock_tickers:
				Avged_Snapshot.pop(Stock_Ticker)

			
			# Put the stocks in a AlpacaInterface friendly fromat
			Return_averaged_Alpaca_compatible_snapshot = []
			for Stock_Ticker in Avged_Snapshot.keys():
				New_Ticker_name = Stock_Ticker[1:]
				Stock_Percent_Of_Sentiment = Avged_Snapshot[Stock_Ticker]['total_sentiment']/total_sentiment_of_positive_stocks
				New_Stock_Format = [New_Ticker_name, Stock_Percent_Of_Sentiment]
				Return_averaged_Alpaca_compatible_snapshot.append([New_Ticker_name, New_Stock_Format])

			print(Return_averaged_Alpaca_compatible_snapshot)

			AlpacaInterface.redistribute(Return_averaged_Alpaca_compatible_snapshot)

			print(f"#########################\n#\n#\n#\nREINVESTING MONEY\n#\n#\n{Return_averaged_Alpaca_compatible_snapshot}\n#\n#\n#\n#\n#########################")



class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)


