import click
import json

from .db import Tweet


class ImportExport:
    def __init__(self, common, twitter=None):
        self.common = common
        self.twitter = twitter

    def excluded_export(self, filename):
        tweets = self.common.session.query(Tweet) \
            .filter(Tweet.user_id == int(self.common.settings.get('user_id'))) \
            .filter(Tweet.exclude_from_delete == 1) \
            .order_by(Tweet.created_at) \
            .all()

        tweets_to_exclude = []
        for tweet in tweets:
            tweets_to_exclude.append(tweet.status_id)

        with open(filename, 'w') as f:
            f.write(json.dumps(tweets_to_exclude))

        click.echo('Exported {} tweet status_ids'.format(len(tweets_to_exclude)))

    def excluded_import(self, filename):
        with open(filename, 'r') as f:
            try:
                status_ids = json.loads(f.read())
            except:
                click.echo('Error JSON decoding input file')
                return

        # Validate
        if type(status_ids) != list:
            click.echo('Input file should be a list')
            return
        for status_id in status_ids:
            if type(status_id) != int:
                click.echo('All items in the input file list should be ints')
                return

        # Import
        for status_id in status_ids:
            tweet = self.common.session.query(Tweet).filter_by(status_id=status_id).first()
            if tweet:
                tweet.exclude_from_delete = True
                self.common.session.add(tweet)
                tweet.excluded_summarize()
            else:
                try:
                    status = self.twitter.api.get_status(status_id)
                    tweet = Tweet(status)
                    tweet.exclude_from_delete = True
                    self.common.session.add(tweet)
                    tweet.excluded_fetch_summarize()
                except tweepy.error.TweepError as e:
                    click.echo('Error for tweet {}: {}'.format(tweet.status_id, e))

        self.common.session.commit()
