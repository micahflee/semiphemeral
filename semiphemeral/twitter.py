import tweepy
import json
import click

from .db import Tweet


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
        ).pages(1):
            fetched_count = 0

            # Import these tweets, and all their threads
            for status in page:
                fetched_count += self.import_tweet(Tweet(status))

                # Only commit every 20 tweets
                if fetched_count % 20 == 0:
                    self.session.commit()

            # Commit the leftovers
            self.session.commit()

        """
        # All done, update the since_id
        tweet = self.session.query(Tweet).order_by(Tweet.status_id.desc()).first()
        if tweet:
            new_since_id = tweet.status_id
            self.settings.set('since_id', new_since_id)
            self.settings.save()
        """

    def import_tweet(self, tweet):
        """
        This imports a tweet, and recursively imports all tweets that it's in reply to,
        and returns the number of tweets fetched
        """
        fetched_count = 0

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
                status = self.api.get_status(tweet.in_reply_to_status_id)
                fetched_count += self.import_tweet(Tweet(status))

        return fetched_count

    def delete(self):
        if not self.authenticated:
            return

        click.echo('Not implemented yet')
