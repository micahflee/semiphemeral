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

        # Fetch tweets
        count = 0
        for status in tweepy.Cursor(
            self.api.user_timeline,
            id=self.settings.get('username'),
            since_id=since_id
        ).items(20):
            # Fetch the tweet
            tweet = Tweet(status)

            # Skip tweets that are already in the database
            if not tweet.already_saved(self.session):
                tweet.summarize()
                self.session.add(tweet)

            # Only commit every 20 tweets
            count += 1
            if count % 20 == 0:
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


    def delete(self):
        if not self.authenticated:
            return

        click.echo('Not implemented yet')
