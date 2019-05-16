import tweepy
import click
import json
from datetime import datetime

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

    def fetch(self):
        if not self.authenticated:
            return

        # See if we retrieve all tweets, or just tweets since the last fetch
        since_id = self.settings.get('since_id')

        if since_id:
            click.secho('Fetching all recent tweets', bold=True)
        else:
            click.secho('Fetching all tweets, this first run may take a long time', bold=True)

        # Fetch tweets a page at a time
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

        # All done, update the since_id
        tweet = self.session.query(Tweet).order_by(Tweet.status_id.desc()).first()
        if tweet:
            self.settings.set('since_id', tweet.status_id)
            self.settings.save()

        self.settings.set('last_fetch', datetime.today().strftime('%Y-%m-%d %I:%M%p'))
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
            tweet.summarize()
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

    def delete(self):
        if not self.authenticated:
            return

        click.echo('Not implemented yet')
