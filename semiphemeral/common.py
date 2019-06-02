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
