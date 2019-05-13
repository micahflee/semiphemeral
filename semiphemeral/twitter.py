import tweepy
import json
import time

from .db import Tweet


class Twitter(object):
    def __init__(self, settings, session):
        self.settings = settings
        self.session = session

        self.authenticated = False

        if not self.settings.is_configured():
            print('Twitter API is not configured yet, configure it with --configure')
            return

        auth = tweepy.OAuthHandler(
            self.settings.get('api_key'),
            self.settings.get('api_secret'))
        auth.set_access_token(
            self.settings.get('access_token_key'),
            self.settings.get('access_token_secret'))
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.authenticated = True

    def fetch(self):
        if not self.authenticated:
            return

        """
        for status in tweepy.Cursor(self.api.user_timeline, screen_name='@realDonaldTrump').items(1):
            print(type(status))

            for k in ['author', 'contributors', 'coordinates', 'created_at', 'destroy', 'entities', 'favorite', 'favorite_count', 'favorited', 'geo', 'id', 'id_str', 'in_reply_to_screen_name', 'in_reply_to_status_id', 'in_reply_to_status_id_str', 'in_reply_to_user_id', 'in_reply_to_user_id_str', 'is_quote_status', 'lang', 'parse', 'parse_list', 'place', 'retweet', 'retweet_count', 'retweeted', 'retweets', 'source', 'source_url', 'text', 'truncated', 'user']:
                print(k, getattr(status, k))
                print('')

        print('Getting 200 tweets')
        tweets = self.api.GetUserTimeline(
            user_id=self.user.id,
            since_id=since_id,
            count=100,
            include_rts=True,
            trim_user=True,
            exclude_replies=False)

        for api_data in tweets:
            #print(json.dumps(api_data.AsDict(), indent=2))
            print(api_data.user.id)
            #tweet = Tweet(api_data)
            #self.session.add(tweet)
        #self.session.commit()
        """


    def delete(self):
        if not self.authenticated:
            return

        print('Not implemented yet')
