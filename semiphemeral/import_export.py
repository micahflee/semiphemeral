import click
import json

from .db import Tweet


class ImportExport:
    def __init__(self, common):
        self.common = common

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
        pass
