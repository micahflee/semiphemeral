import tweepy
import click
import json
import datetime

from .db import Tweet, Thread


class Twitter(object):
    def __init__(self, settings, session):
        self.settings = settings
        self.session = session

        self.authenticated = False

        if not self.settings.is_configured():
            click.echo('Twitter API is not configured yet, configure it with --configure')
            return

        auth = tweepy.OAuthHandler(
            self.settings.get('api_key'),
            self.settings.get('api_secret'))
        auth.set_access_token(
            self.settings.get('access_token_key'),
            self.settings.get('access_token_secret'))
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.authenticated = True

        # Make sure we've saved the user id
        user = self.api.get_user(self.settings.get('username'))
        if user:
            self.settings.set('user_id', user.id)
            self.settings.save()

        # Date format for saving last_fetch setting
        self.last_fetch_format = '%Y-%m-%d %I:%M%p'

    def fetch(self):
        if not self.authenticated:
            return

        if self.settings.get('delete_tweets'):
            # We fetch tweets since the last fetch (or all tweets, if it's None)
            since_id = self.settings.get('since_id')
            if since_id:
                click.secho('Fetching all recent tweets', fg='cyan')
            else:
                click.secho('Fetching all tweets, this first run may take a long time', fg='cyan')

            # Fetch tweets from timeline a page at a time
            for page in tweepy.Cursor(
                self.api.user_timeline,
                id=self.settings.get('username'),
                since_id=since_id
            ).pages():
                fetched_count = 0

                # Import these tweets, and all their threads
                for status in page:
                    fetched_count += self.import_tweet(Tweet(status))

                    # Only commit every 20 tweets
                    if fetched_count % 20 == 0:
                        self.session.commit()

                # Commit the leftovers
                self.session.commit()

                # Now hunt for threads. This is a dict that maps the root status_id
                # to a list of status_ids in the thread
                threads = {}
                for status in page:
                    if status.in_reply_to_status_id:
                        status_ids = self.calculate_thread(status.id)
                        root_status_id = status_ids[0]
                        if root_status_id in threads:
                            for status_id in status_ids:
                                if status_id not in threads[root_status_id]:
                                    threads[root_status_id].append(status_id)
                        else:
                            threads[root_status_id] = status_ids

                # For each thread, does this thread already exist, or do we create a new one?
                for root_status_id in threads:
                    status_ids = threads[root_status_id]
                    thread = self.session.query(Thread).filter_by(root_status_id=root_status_id).first()
                    if not thread:
                        thread = Thread(root_status_id)
                        count = 0
                        for status_id in status_ids:
                            tweet = self.session.query(Tweet).filter_by(status_id=status_id).first()
                            if tweet:
                                thread.tweets.append(tweet)
                                count += 1
                        if count > 0:
                            click.echo('Added new thread with {} tweets (root id={})'.format(count, root_status_id))
                    else:
                        count = 0
                        for status_id in status_ids:
                            tweet = self.session.query(Tweet).filter_by(status_id=status_id).first()
                            if tweet and tweet not in thread.tweets:
                                thread.tweets.append(tweet)
                                count += 1
                        if count > 0:
                            click.echo('Added {} tweets to existing thread (root id={})'.format(count, root_status_id))
                    self.session.commit()

            # It appears that twitter will only return the last 4000 likes. So if
            # it's been over a day since the last fetch, try fetching all likes again
            like_since_id = since_id
            last_fetch_str = self.settings.get('last_fetch')
            if last_fetch_str:
                last_fetch = datetime.datetime.strptime(last_fetch_str, self.last_fetch_format)
                now = datetime.datetime.now()
                if now - last_fetch > datetime.timedelta(days=1):
                    like_since_id = None

            # Fetch tweets that are liked
            click.secho('Fetching tweets that you liked', fg='cyan')
            for page in tweepy.Cursor(
                self.api.favorites,
                id=self.settings.get('username'),
                since_id=like_since_id
            ).pages():
                # Import these tweets
                for status in page:
                    tweet = Tweet(status)
                    if not tweet.already_saved(self.session):
                        tweet.fetch_summarize()
                        self.session.add(tweet)
                # Commit a page of tweets at a time
                self.session.commit()

            # All done, update the since_id
            tweet = self.session.query(Tweet).order_by(Tweet.status_id.desc()).first()
            if tweet:
                self.settings.set('since_id', tweet.status_id)
                self.settings.save()

        # Calculate which threads should be excluded from deletion
        self.calculate_excluded_threads()

        self.settings.set('last_fetch', datetime.datetime.today().strftime(self.last_fetch_format))
        self.settings.save()

    def calculate_thread(self, status_id):
        """
        Given a tweet, recursively add its parents to a thread. In this end, the first
        element of the list should be the root of the thread
        """
        tweet = self.session.query(Tweet).filter_by(status_id=status_id).first()
        if not tweet:
            return []
        if not tweet.in_reply_to_status_id:
            return [status_id]
        return self.calculate_thread(tweet.in_reply_to_status_id) + [status_id]

    def import_tweet(self, tweet):
        """
        This imports a tweet, and recursively imports all tweets that it's in reply to,
        and returns the number of tweets fetched
        """
        fetched_count = 0

        # Save the tweet, if it's not already saved
        if not tweet.already_saved(self.session):
            tweet.fetch_summarize()
            fetched_count += 1
            self.session.add(tweet)

        # Is this tweet a reply?
        if tweet.in_reply_to_status_id:
            # Do we already have the parent tweet?
            parent_tweet = self.session.query(Tweet).filter_by(status_id=tweet.in_reply_to_status_id).first()
            if not parent_tweet:
                # If not, import it
                try:
                    status = self.api.get_status(tweet.in_reply_to_status_id)
                    fetched_count += self.import_tweet(Tweet(status))
                except tweepy.error.TweepError:
                    # If it's been deleted, ignore
                    pass

        return fetched_count

    def calculate_excluded_threads(self):
        """
        Based on the current settings, figure out which threads should be excluded from
        deletion, and which threads should have their tweets deleted
        """
        click.secho('Calculating which threads should be excluded', fg='cyan')

        # Reset the should_exclude flag for all threads
        self.session.query(Thread).update({"should_exclude": False})
        self.session.commit()

        # Set should_exclude for all threads based on the settings
        if self.settings.get('tweets_threads_threshold'):
            threads = self.session.query(Thread).join(Thread.tweets, aliased=True) \
                .filter(Tweet.user_id == int(self.settings.get('user_id'))) \
                .filter(Tweet.is_deleted == 0) \
                .filter(Tweet.is_retweet == 0) \
                .filter(Tweet.retweet_count >= self.settings.get('tweets_retweet_threshold')) \
                .filter(Tweet.favorite_count >= self.settings.get('tweets_like_threshold')) \
                .all()
            for thread in threads:
                thread.should_exclude = True
            self.session.commit()

    def delete(self):
        if not self.authenticated:
            return

        # First, run fetch
        click.secho('Before deleting anything, fetch', fg='cyan')
        #self.fetch()

        # Unretweet and unlike tweets
        if self.settings.get('retweets_likes'):
            # Unretweet
            if self.settings.get('retweets_likes_delete_retweets'):
                datetime_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=self.settings.get('retweets_likes_retweets_threshold'))
                tweets = self.session.query(Tweet) \
                    .filter(Tweet.user_id == int(self.settings.get('user_id'))) \
                    .filter(Tweet.is_deleted == 0) \
                    .filter(Tweet.is_retweet == 1) \
                    .filter(Tweet.created_at < datetime_threshold) \
                    .order_by(Tweet.created_at) \
                    .all()

                click.secho('Deleting {} retweets, starting with the earliest'.format(len(tweets)), fg='cyan')
                click.echo('(not implemented yet)')

                count = 0
                for tweet in tweets:
                    #self.api.destroy_status(tweet.status_id)
                    tweet.unretweet_summarize()
                    #tweet.is_deleted = True
                    #self.session.add(tweet)

                    count += 1
                    if count % 20 == 0:
                        self.session.commit()

                    if count == 2:
                        break

                self.session.commit()

            # Unlike
            if self.settings.get('retweets_likes_delete_likes'):
                datetime_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=self.settings.get('retweets_likes_likes_threshold'))
                tweets = self.session.query(Tweet) \
                    .filter(Tweet.user_id != int(self.settings.get('user_id'))) \
                    .filter(Tweet.is_unliked == 0) \
                    .filter(Tweet.favorited == True) \
                    .filter(Tweet.created_at < datetime_threshold) \
                    .order_by(Tweet.created_at) \
                    .all()

                click.secho('Unliking {} tweets, starting with the earliest'.format(len(tweets)), fg='cyan')
                click.echo('(not implemented yet)')

                count = 0
                for tweet in tweets:
                    #self.api.destroy_favorite(tweet.status_id)
                    tweet.unlike_summarize()
                    #tweet.is_unliked = True
                    #self.session.add(tweet)

                    count += 1
                    if count % 20 == 0:
                        self.session.commit()

                    if count == 2:
                        break

                self.session.commit()

        # Deleting tweets
        if self.settings.get('delete_tweets'):
            datetime_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=self.settings.get('tweets_days_threshold'))
            tweets = self.session.query(Tweet) \
                .filter(Tweet.user_id == int(self.settings.get('user_id'))) \
                .filter(Tweet.is_deleted == 0) \
                .filter(Tweet.is_retweet == 0) \
                .filter(Tweet.created_at < datetime_threshold) \
                .filter(Tweet.retweet_count < self.settings.get('tweets_retweet_threshold')) \
                .filter(Tweet.favorite_count < self.settings.get('tweets_like_threshold')) \
                .filter(Tweet.exclude_from_delete == False) \
                .order_by(Tweet.created_at) \
                .all()

            click.secho('Deleting {} tweets, starting with the earliest'.format(len(tweets)), fg='cyan')
            click.echo('(not implemented yet)')

            count = 0
            for tweet in tweets:
                #self.api.destroy_status(tweet.status_id)
                tweet.delete_summarize()
                #tweet.is_deleted = True
                #self.session.add(tweet)

                count += 1
                if count % 20 == 0:
                    self.session.commit()

                if count == 2:
                    break

            self.session.commit()
