import os
import click

from .common import Common
from .settings import Settings
from .db import create_db
from .web import create_app
from .twitter import Twitter

version = '0.1'


@click.command()
@click.option('--configure', is_flag=True, help='Start the web server to configure semiphemeral')
@click.option('--stats', is_flag=True, help='Show stats about tweets in the database')
@click.option('--fetch', is_flag=True, help='Download all tweets')
@click.option('--delete', is_flag=True, help='Delete tweets that aren\'t automatically or manually excluded')
@click.option('--debug', is_flag=True, help='Start web server in debug mode')
def main(configure, stats, fetch, delete, debug):
    click.echo(click.style("semiphemeral {}".format(version), fg='yellow'))

    # Initialize stuff
    os.makedirs(os.path.expanduser('~/.semiphemeral'), exist_ok=True)
    settings = Settings(os.path.expanduser('~/.semiphemeral/settings.json'))
    session = create_db(os.path.expanduser('~/.semiphemeral/tweets.db'))

    common = Common(settings, session)

    if configure:
        click.echo('Load this website in a browser to configure semiphemeral, and press Ctrl-C when done')
        click.echo('http://127.0.0.1:8080')
        click.echo('')
        app = create_app(common)
        app.run(host='127.0.0.1', port=8080, threaded=False, debug=debug)

    elif stats:
        t = Twitter(common)
        t.stats()

    elif fetch:
        t = Twitter(common)
        if settings.is_configured():
            t.fetch()

    elif delete:
        t = Twitter(common)
        if settings.is_configured():
            t.delete()

    else:
        click.echo('You must choose either --configure, --fetch, or --delete')
