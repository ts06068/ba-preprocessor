from twikit import Client
import twikit
import pymssql
from tqdm import tqdm
import pandas as pd
from time import sleep
from datetime import datetime
import sys

USERNAME = 'y0unwoo88814'
EMAIL = 'y0unwoo_me@naver.com'
PASSWORD = 'Carpediem2002!'

accounts = [
    {'username': 'ts06067',
     'password': 'Carpediem2002!'},
     {'username': 'ts06068',
     'password': 'Dream2002!'},
     {'username': 'y0unwoo88814',
     'password': 'Carpediem2002!'},
     {'username': 'altmetric1001', # y0unwoo88899961, altmetric1001
     'password': 'altmetricpassword'},
     {'username': 'y0unwoo88838011',
     'password': 'Carpediem2002!'},
     {'username': 'altmetric1002', # y0unwoo88843694, altmetric1002
     'password': 'altmetricpassword'},
     {'username': 'altmetric1003', # y0unwoo88856631, altmetric1003
     'password': 'altmetricpassword'},
     {'username': 'altmetric1004', # y0unwoo88881513, altmetric1004
     'password': 'altmetricpassword'}
]

print(f'number of accounts: {len(accounts)}')

idx = int(sys.argv[1])
account = accounts[idx]

client = Client('ko-KR')
client.login(
    auth_info_1=account['username'] ,
    password=account['password']
)

print('log in successful')

server = "localhost"
user = "sa"
password = "Password1!"
db = "ba"

conn = pymssql.connect(server, user, password, database=db, autocommit=True)
cursor = conn.cursor(as_dict=True)

select_mention_query = "select post_external_id, post_date from mention where post_source = 'tweet' order by post_index"
update_mention_query = "update mention set post_date = (%s), tweet_favorite_count = (%s), \
    tweet_full_text = (%s), tweet_text = (%s), tweet_quote_count = (%s), tweet_lang = (%s), \
        tweet_view_count = (%s), tweet_retweet_count = (%s), tweet_reply_count = (%s) where post_external_id = (%s)"

jump = 137500
start_idx = idx*jump
end_idx = start_idx + jump

cursor.execute(select_mention_query)

if idx < 7:
    result = cursor.fetchall()[start_idx:end_idx]
else:
    result = cursor.fetchall()[start_idx:]

df = pd.DataFrame(result)
print(df)

for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    try:
        """
        if row['post_external_id'] is None or row['profile_id'] is None:
            continue
        """
        pub_year = int(row['post_date'].date().year)

        if pub_year > 1900:
            print('\ndate already updated, skip')
            continue

        raw_external_id = row['post_external_id']
        external_id = str.lower(raw_external_id).split('.')[-1]
        #profile_id = str.lower(row['profile_id']).split(':')[-1]

        #url = f'x.com/{external_id}/status/{profile_id}'
        tweet = client.get_tweet_by_id(external_id)

        if tweet is None:
            print('\nno tweet found')
            continue

        created_at = tweet.created_at_datetime
        favorite_count = tweet.favorite_count
        full_text = tweet.full_text
        quote_count = tweet.quote_count
        lang = tweet.lang
        reply_count = tweet.reply_count
        text = tweet.text
        view_count = tweet.view_count
        retweet_count = tweet.retweet_count

        p = (created_at, favorite_count, full_text, text, quote_count, lang, view_count, retweet_count, reply_count, raw_external_id)

        cursor.execute(update_mention_query, p)
    except AttributeError as e:
        print('\nno tweet found')
        continue
    except twikit.errors.TooManyRequests as e:
        print(f'\nWaiting for 15 min... {datetime.now()}')
        sleep(950)
        continue
    except twikit.errors.TweetNotAvailable as e:
        print('\ntweet not available')
        continue
    except pymssql.exceptions.OperationalError as e:
        print(e)
        continue