import datetime

from .db import Tweet, Thread


class Common:
    def __init__(self, settings, session):
        self.settings = settings
        self.session = session

    def get_stats(self):
        self.settings.load()

        is_configured = self.settings.is_configured()
        last_fetch = self.settings.get('last_fetch')
        my_tweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=0 AND is_retweet=0'.format(int(self.settings.get('user_id')))).first()[0]
        my_retweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=0 AND is_retweet=1'.format(int(self.settings.get('user_id')))).first()[0]
        my_likes = self.session.execute('SELECT COUNT(*) FROM tweets WHERE favorited=1').first()[0]
        deleted_tweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=0'.format(int(self.settings.get('user_id')))).first()[0]
        deleted_retweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=1'.format(int(self.settings.get('user_id')))).first()[0]
        unliked_tweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE favorited=1 AND is_unliked=1').first()[0]
        excluded_tweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND exclude_from_delete=1'.format(int(self.settings.get('user_id')))).first()[0]
        other_tweets = self.session.execute('SELECT COUNT(*) FROM tweets WHERE user_id!={}'.format(int(self.settings.get('user_id')))).first()[0]
        threads = self.session.execute('SELECT COUNT(*) FROM threads').first()[0]

        return {
            'is_configured': is_configured,
            'last_fetch': last_fetch,
            'my_tweets': my_tweets,
            'my_retweets': my_retweets,
            'my_likes': my_likes,
            'deleted_tweets': deleted_tweets,
            'deleted_retweets': deleted_retweets,
            'unliked_tweets': unliked_tweets,
            'excluded_tweets': excluded_tweets,
            'other_tweets': other_tweets,
            'threads': threads
        }

    def get_tweets_to_delete(self, include_excluded=False):
        """
        Returns a list of Tweet objects for tweets that should be deleted based
        on criteria in settings. This list includes tweets where exclude_from_delete=True,
        so it's important to manually exclude those before deleting
        """
        self.settings.load()
        datetime_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=self.settings.get('tweets_days_threshold'))

        # Select tweets from threads to exclude
        tweets_to_exclude = []
        threads = self.session.query(Thread) \
            .filter(Thread.should_exclude == True) \
            .all()
        for thread in threads:
            for tweet in thread.tweets:
                if tweet.user_id == self.settings.get('user_id'):
                    tweets_to_exclude.append(tweet.status_id)

        # Select tweets that we will delete
        tweets_to_delete = []
        q = self.session.query(Tweet) \
            .filter(Tweet.user_id == int(self.settings.get('user_id'))) \
            .filter(Tweet.is_deleted == 0) \
            .filter(Tweet.is_retweet == 0) \
            .filter(Tweet.created_at < datetime_threshold) \
            .filter(Tweet.retweet_count < self.settings.get('tweets_retweet_threshold')) \
            .filter(Tweet.favorite_count < self.settings.get('tweets_like_threshold'))

        # Should we also filter out exclude_from_delete?
        if not include_excluded:
            q = q.filter(Tweet.exclude_from_delete != True)

        q = q.order_by(Tweet.created_at)

        tweets = q.all()
        for tweet in tweets:
            if tweet.status_id not in tweets_to_exclude:
                tweets_to_delete.append(tweet)

        return tweets_to_delete
