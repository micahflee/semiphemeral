import os
import click
import json

from .common import Common
from .settings import Settings
from .db import create_db
from .web import create_app
from .twitter import Twitter
from .import_export import ImportExport

version = "0.7"


def init():
    click.echo(click.style("semiphemeral {}".format(version), fg="yellow"))

    # Initialize stuff
    base = os.path.expanduser("~/.semiphemeral")
    os.makedirs(base, mode=0o700, exist_ok=True)
    # Fix insecure prior installation permissions
    os.chmod(base, 0o700)
    settings = Settings(os.path.join(base, "settings.json"))
    session = create_db(os.path.join(base, "tweets.db"))

    common = Common(settings, session)
    return common


@click.group()
def main():
    """Automatically delete your old tweets, except for the ones you want to keep"""


@main.command("configure", short_help="Start the web server to configure semiphemeral")
@click.option("--debug", is_flag=True, help="Start web server in debug mode")
@click.option("--host", default="127.0.0.1", help="Host to expose the web server on")
@click.option("--port", default=8080, help="Port to expose the web server on")
def configure(debug, host, port):
    common = init()
    click.echo(
        "Load this website in a browser to configure semiphemeral, and press Ctrl-C when done"
    )
    click.echo("http://{host}:{port}".format(host=host, port=port))
    click.echo("")
    app = create_app(common)
    app.run(host=host, port=port, threaded=False, debug=debug)


@main.command("stats", short_help="Show stats about tweets in the database")
def stats():
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        t.stats()


@main.command("fetch", short_help="Download all tweets/DMs")
def fetch():
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        t.fetch()


@main.command(
    "delete",
    short_help="Delete tweets that aren't automatically or manually excluded, likes, and DMs",
)
def delete():
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        t.delete()

@main.command('import', short_help='Import tweets from a Twitter archive export')
@click.argument('path', type=click.Path(exists=True))
def archive_import(path):
    common = init()
    t = Twitter(common)
    t.import_dump(path)


@main.command(
    "unlike",
    short_help="Delete old likes that aren't available through the Twitter API",
)
@click.option(
    "--filename",
    required=True,
    help="Path to like.js from Twitter archive downloaded from https://twitter.com/settings/your_twitter_data",
)
def unlike(filename):
    common = init()

    t = Twitter(common)
    if common.settings.is_configured():
        t.unlike(filename)


@main.command(
    "delete_dms", short_help="Delete DMs that aren't available through the Twitter API"
)
@click.option(
    "--filename",
    required=True,
    help="Path to direct-message.js from Twitter archive downloaded from https://twitter.com/settings/your_twitter_data",
)
def delete_dms(filename):
    common = init()

    t = Twitter(common)
    if common.settings.is_configured():
        t.delete_dms(filename)


@main.command(
    "excluded_export",
    short_help="Export tweets excluded that are excluded from deletion",
)
@click.option(
    "--filename",
    required=True,
    help="Output JSON file to save a list of tweet status_ids",
)
def excluded_export(filename):
    common = init()
    ie = ImportExport(common)
    ie.excluded_export(filename)


@main.command(
    "excluded_import",
    short_help="Import tweets excluded that are excluded from deletion",
)
@click.option(
    "--filename",
    required=True,
    help="Input JSON file that contains a list of tweet status_ids",
)
def excluded_import(filename):
    common = init()
    t = Twitter(common)
    if common.settings.is_configured():
        ie = ImportExport(common, t)
        ie.excluded_import(filename)
