import tweepy
from tweepy import OAuthHandler
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import csv
import numpy as np
import time
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
#from nltk.sentiment.util import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

api_key = '8J1Xhsz5CpJ03ZgKU6lIaUSn0'
api_key_secret = '21sGnOEoPkr1C3LHvQkngqPrz2b4H1XJ80rwOdzf4GQLOQoU4y'
access_token = '728490112204558336-nkbo0b0p4l5DuP9NRkriAoVgqPvAZOj'
access_token_secret = 'tmsyHjL0TtxhwcciXZt8XqzxoHr7DWueOaCaMuiFd4ju2'

# authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,wait_on_rate_limit=True)
public_tweets = api.home_timeline()

count =   20000

df1 = pd.DataFrame()

#try:
    # Creation of query method using appropriate parameters
tweets = tweepy.Cursor(api.search_tweets,q="bitcoin", until="2022-01-14").items(count)

# Pulling information from tweets iterable object and adding relevant tweet information in our data frame
for tweet in tweets:
    df1 = df1.append(
                      {'Created at' : tweet._json['created_at'],
                                    'User ID': tweet._json['id'],
                          'User Name': tweet.user._json['name'],
                                    'Text': tweet._json['text'],
                  'Description': tweet.user._json['description'],
                        'Location': tweet.user._json['location'],
          'Followers Count': tweet.user._json['followers_count'],
              'Friends Count': tweet.user._json['friends_count'],
            'Statuses Count': tweet.user._json['statuses_count'],
      'Profile Image Url': tweet.user._json['profile_image_url'],
                      }, ignore_index=True)
#except BaseException as e:
 #   print('failed on_status,',str(e))
   # time.sleep(3)

df1.rename(columns={'Created at':'timestamp','User ID':'id','Text': 'text'}, inplace=True)

df1["timestamp"] = df1["timestamp"].astype('datetime64[ns]') 
df1["timestamp"] = df1.timestamp.dt.to_pydatetime()

tweet_df = df1

# Removal of rows with promotion posts words
tweet_df = tweet_df[~tweet_df.text.str.contains("GIVEAWAY")]
tweet_df = tweet_df[~tweet_df.text.str.contains("FREE")]
tweet_df = tweet_df[~tweet_df.text.str.contains("giveaway")]
tweet_df = tweet_df[~tweet_df.text.str.contains("free")]


# Remove numbers
tweet_df.text = tweet_df.text.str.replace('\d+', '')

# Decapitalize
tweet_df.text = tweet_df.text.str.lower()

# Remove URLS
tweet_df.text = tweet_df.text.apply(lambda x:re.sub(r"http\S+", "", str(x)))

# Remove handlers
tweet_df.text = tweet_df.text.apply(lambda x:re.sub('@[^\s]+','',str(x)))

# Remove all the special characters
tweet_df.text = tweet_df.text.apply(lambda x:' '.join(re.findall(r'\w+', x)))

# Remove all single characters
tweet_df.text = tweet_df.text.apply(lambda x:re.sub(r'\s+[a-zA-Z]\s+',' ', x))

# Substituting multiple spaces with single space
tweet_df.text = tweet_df.text.apply(lambda x:re.sub(r'\s+', ' ', x, flags=re.I))

# Removing stopwords
stop = stopwords.words('english')
tweet_df.text = tweet_df.text.apply(lambda x: ' '.join([word for word in word_tokenize(x) if word not in (stop)]))

sid = SentimentIntensityAnalyzer()

def get_sentiment(row, **kwargs):
    sentiment_score = sid.polarity_scores(row)
    positive_meter = (sentiment_score['pos'])
    negative_meter = (sentiment_score['neg'])
    return positive_meter if kwargs['k'] == 'positive' else negative_meter

# Applying sentiment to non-lemmatized df
tweet_df['positive'] = tweet_df.text.apply(get_sentiment, k='positive')
tweet_df['negative'] = tweet_df.text.apply(get_sentiment, k='negative')

# Rename id to to numberoftweets
tweet_df.rename(columns={'id': 'numberoftweets'}, inplace=True)

# Combining negative and positive sentiment to get one sentiment column
tweet_df["sentiment"] = tweet_df["positive"] - tweet_df["negative"]

tweet_df['timestamp'] = pd.to_datetime(tweet_df['timestamp'])

# Aggregate data by the day
tweet_dfa = tweet_df.resample('D', on='timestamp').agg({'numberoftweets':'nunique','sentiment':'mean'})

tweet_dfa = tweet_dfa.reset_index()
tweet_dfa.reset_index(inplace=True)
tweet_dfa.drop('index', axis=1, inplace=True)

# get yesterday's date
d = datetime.today()
d = d
d = d.strftime('%Y-%m-%d')

# Get Bitcoin data
price_df = yf.download(tickers='BTC-USD', start = d, end = d)

price_df = price_df.reset_index()
price_df.reset_index(inplace=True)
price_df.drop('index', axis=1, inplace=True)

price_df.rename(columns={'Date': 'timestamp'}, inplace=True)

# Join price df with twitter df
df = pd.merge(tweet_dfa, price_df, on='timestamp',  how='right')

df.to_csv('database.csv', mode='a', header=True)