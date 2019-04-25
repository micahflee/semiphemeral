# ephemeral

Delete old tweets based on specific criteria

## Twitter API credentials

To use this tool, the following environment variables need to exist:

```
TWITTER_API_KEY
TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN_KEY
TWITTER_ACCESS_TOKEN_SECRET
```

See [here](https://python-twitter.readthedocs.io/en/latest/getting_started.html) for some documentation on how to get these values from Twitter.

## Usage

```
ephemeral USERNAME
```

## Development

Make sure you have [pipenv](https://pipenv.readthedocs.io/en/latest/). Then install dependencies:

```sh
pipenv install --dev
```

And run the program like this:

```sh
pipenv run python -c 'import ephemeral; ephemeral.main()'
```
