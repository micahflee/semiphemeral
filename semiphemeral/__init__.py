import os
import click

from .common import Common
from .settings import Settings
from .db import create_db
from .web import create_app
from .twitter import Twitter

version = '0.3'


def init():
    click.echo(click.style("semiphemeral {}".format(version), fg='yellow'))

    # Initialize stuff
    os.makedirs(os.path.expanduser('~/.semiphemeral'), exist_ok=True)
    settings = Settings(os.path.expanduser('~/.semiphemeral/settings.json'))
    session = create_db(os.path.expanduser('~/.semiphemeral/tweets.db'))

    common = Common(settings, session)
    return common


@click.group()
def main():
    """Automatically delete your old tweets, except for the ones you want to keep"""


@main.command('configure', short_help='Start the web server to configure semiphemeral')
def configure(debug=False):
    common = init()
    click.echo('Load this website in a browser to configure semiphemeral, and press Ctrl-C when done')
    click.echo('http://127.0.0.1:8080')
    click.echo('')
    app = create_app(common)
    app.run(host='127.0.0.1', port=8080, threaded=False)


@main.command('stats', short_help='Show stats about tweets in the database')
def stats():
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        t.stats()


@main.command('fetch', short_help='Download all tweets')
def fetch():
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        t.fetch()


@main.command('delete', short_help='Delete tweets that aren\'t automatically or manually excluded')
def delete():
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        t.delete()
