import tweepy
import json
import datetime
import time

time.sleep(3)

#Sentiment Analyzer

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()


# Importing Keys

with open('keys.json') as keysfile:
	keys = json.load(keysfile)


#adding support for sentiment analysis of multiple stoinks

Total = {
	"total_sentiment": 0.0,
	"Stocks_analized": 0
}

Stocks = {
	"$GME": {
		"total_sentiment": 0.0,
		"Stocks_analized": 0
	},
	"$AMC": {
		"total_sentiment": 0.0,
		"Stocks_analized": 0
	},
	"$NOK": {
		"total_sentiment": 0.0,
		"Stocks_analized": 0
	},
	"$BB": {
		"total_sentiment": 0.0,
		"Stocks_analized": 0
	}
}




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



class MyStreamListener(tweepy.StreamListener):

	def on_status(self, status):
		Start_time_of_analysis = time.time() 
		text = get_status_full_text(status)
		print("##########################")
		print(text)
		print("## SENTAMINT ##")

		sentiment = analyzer.polarity_scores(text) #create custom popularity score if 🚀 set compound == 0.7

		global Stocks
		global Total

		Total["Stocks_analized"] += 1
		Total["total_sentiment"] += sentiment['compound']

		for Stock_ticker in Stocks.keys():
			if Stock_ticker in text.split(' '):
				Stocks[Stock_ticker]["Stocks_analized"] += 1
				Stocks[Stock_ticker]["total_sentiment"] += sentiment['compound']

		print(f"Tweet's Sentiment:          {sentiment}")
		print(f"Amount of tweets analyzed:  {Total['Stocks_analized']}")
		print(f"Sum of all tweet sentiment: {Total['total_sentiment']}")

		End_time_of_analysis = time.time() 
		print(f"Time to analyze in milli  : {(End_time_of_analysis-Start_time_of_analysis) * 1000.0}")
		print("##########################")


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener, tweet_mode="extended")
myStream.filter(track=['$GME', '$AMC', '$NOK', '$BB'], is_async=True)



"""def GetStockSentimentOnDay(Stock_name, Sample_size, Day):
	start_date = Day
	end_date = Day + datetime.timedelta(days=1)
	tweets_abt_stock = api.search("$GME", lang='en', result_type="popular", count=1, since=start_date, until=end_date, tweet_mode="extended")
	print(tweets_abt_stock.next_results)

	def run_func_on_all_tweets_for_day(queryed_statuses, max_tweets, func_to_run):
		tweets_ran = 0

		for tweet in queryed_statuses:
			func_to_run(tweet)
			tweets_ran += 1
		
		if queryed_statuses.next_results != None or tweets_ran >= max_tweets:
			run_func_on_all_tweets_for_day(queryed_statuses, max_tweets, func_to_run)
		else:
			print(f"Hit end of tweets, ran {tweets_ran} tweets")
		
	def analyze_tweet_sentiment(tweet):
		text = tweet.full_text
		ps = analyzer.polarity_scores(text)
		print(text, ps)

	run_func_on_all_tweets_for_day(tweets_abt_stock, 1, analyze_tweet_sentiment)

	

GetStockSentimentOnDay(1,1,datetime.date(2021,1,30))
"""