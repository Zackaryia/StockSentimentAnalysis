import tweepy
import json
import datetime

#Sentiment Analyzer

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()


# Importing Keys

with open('keys.json') as keysfile:
	keys = json.load(keysfile)


# Setting up Tweepy (Twitter API Wrapper for python)

auth = tweepy.OAuthHandler(keys['API_Key'], keys['API_Secret_Key'])
auth.set_access_token(keys['Access_Token'], keys['Access_Token_Secret'])

api = tweepy.API(auth)

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
		print("##########################")
		print(get_status_full_text(status))
		print("##########################")

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener, tweet_mode="extended")
myStream.filter(track=['$GME'], is_async=True)



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