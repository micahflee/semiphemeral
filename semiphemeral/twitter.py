import twitter

from .db import Tweet


class Twitter(object):
    def __init__(self, settings, session):
        self.settings = settings
        self.session = session

        self.authenticated = False

        if not self.settings.is_configured():
            print('Twitter API is not configured yet, configure it with --configure')
            return

        self.api = twitter.Api(consumer_key=self.settings.get('api_key'),
            consumer_secret=self.settings.get('api_secret'),
            access_token_key=self.settings.get('access_token_key'),
            access_token_secret=self.settings.get('access_token_secret'),
            sleep_on_rate_limit=True)
        self.authenticated = True

        self.user = self.api.GetUser(screen_name=self.settings.get('username'))

    def fetch(self):
        if not self.authenticated:
            return

        tweet = self.session.query(Tweet).order_by(Tweet.tweet_id.desc()).first()
        if tweet:
            since_id = tweet.tweet_id
        else:
            since_id = None

        # Start fetching
        print('Getting 100 tweets')
        tweets = self.api.GetUserTimeline(
            user_id=self.user.id,
            since_id=since_id,
            count=100,
            include_rts=True,
            trim_user=True,
            exclude_replies=False)
        for api_data in tweets:
            tweet = Tweet(api_data)
            self.session.add(tweet)
            print(tweet.text)
        self.session.commit()

    def delete(self):
        if not self.authenticated:
            return

        print('Not implemented yet')
