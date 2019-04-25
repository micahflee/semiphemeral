import os
import sys
import click
import twitter

version = '0.1'


def validate_environment():
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN_KEY',
        'TWITTER_ACCESS_TOKEN_SECRET'
    ]
    found = True
    for var in required_vars:
        if var not in os.environ:
            found = False
    return found


@click.command()
@click.argument('username')
def main(username):
    click.echo(click.style("ephemeral {}".format(version), fg='yellow'))

    # Make sure environment variables are set
    if not validate_environment():
        click.echo(click.style("These environment variables must be exist:", fg='red'))
        click.echo(click.style("TWITTER_API_KEY", fg='red'))
        click.echo(click.style("TWITTER_API_SECRET", fg='red'))
        click.echo(click.style("TWITTER_ACCESS_TOKEN_KEY", fg='red'))
        click.echo(click.style("TWITTER_ACCESS_TOKEN_SECRET", fg='red'))
        sys.exit(1)

    # Authenticate to the twitter API
    api = twitter.Api(consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_SECRET'],
        access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

    # Get the user
    user = api.GetUser(screen_name=username)
    print(user)
