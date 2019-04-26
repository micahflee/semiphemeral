import os
import sys
import click
import twitter

from .db import create_db
from .web import create_app
from .settings import Settings

version = '0.1'


@click.command()
@click.option('--configure', is_flag=True, help='Start the web server to configure ephemeral')
@click.option('--debug', is_flag=True, help='Start web server in debug mode')
def main(configure, debug):
    click.echo(click.style("ephemeral {}".format(version), fg='yellow'))

    # Initialize stuff
    os.makedirs(os.path.expanduser('~/.ephemeral'), exist_ok=True)
    settings = Settings(os.path.expanduser('~/.ephemeral/settings.json'))
    session = create_db(os.path.expanduser('~/.ephemeral/tweets.db'))

    if configure:
        click.echo('Load this website in a browser to configure ephemeral')
        click.echo('http://127.0.0.1:8080')
        click.echo('')
        app = create_app(settings, session)
        app.run(host='127.0.0.1', port=8080, debug=debug)

    else:
        click.echo('Only --configure is implemented so far')

    """
    # Authenticate to the twitter API
    api = twitter.Api(consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_SECRET'],
        access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

    # Get the user
    username = "micahflee"
    user = api.GetUser(screen_name=username)
    statuses = api.GetUserTimeline(user.id)
    print(statuses[6])
    """
