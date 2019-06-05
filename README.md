# Semiphemeral

There are plenty of tools that let you make your Twitter feed ephemeral, automatically deleting tweets older than some threshold, like one month.

Semiphemeral does this, but also lets you automatically exclude tweets based on criteria: how many RTs or likes they have, and if they're part of a thread where one of your tweets has that many RTs or likes. It also lets you manually select tweets you'd like to exclude from deleting.

~~It can also automatically delete your old direct messages.~~ (DM support is currently [broken](https://github.com/tweepy/tweepy/issues/1081) in tweepy, I'm gonna wait until it's fixed first.)

## Installation

```
pip3 install semiphemeral
```

## How it works

Semiphemeral is a command line tool that you run locally on your computer, or on a server.

```
$ semiphemeral
Usage: app.py [OPTIONS] COMMAND [ARGS]...

  Automatically delete your old tweets, except for the ones you want to keep

Options:
  --help  Show this message and exit.

Commands:
  configure  Start the web server to configure semiphemeral
  delete     Delete tweets that aren't automatically or manually excluded
  fetch      Download all tweets
  stats      Show stats about tweets in the database
```

Start by running `semiphemeral configure`, which starts a local web server at http://127.0.0.1:8080/. Load that website in a browser.

You must supply Twitter API credentials here, which you can get by following [this guide](https://python-twitter.readthedocs.io/en/latest/getting_started.html) (basically, you need to login to https://developer.twitter.com/ and create a new "Twitter app" that only you will be using).

From the settings page you also tell semiphemeral which tweets to exclude from deletion:

![Settings](/screenshots/settings.png)

Once you have configured semiphemeral, fetch all of the tweets from your account by running `semiphemeral fetch`. (It may take a long time if you have a lot of tweets -- when semiphemeral hits a Twitter rate limit, it just waits the shortest amount of time allowed until it can continue fetching.)

Then go back to the configuration web app and look at the tweets page. From here, you can look at all of the tweets that are going to get deleted the next time you run `semiphemeral delete`, and choose to manually exclude some of them from deletion. This interface paginates all of the tweets that are staged for deletion, and allows you to filter them by searching for phrases in the text of your tweets.

Once you have chosen all tweets you want to exclude, you may want to [download your Twitter archive](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive) for your records.

Then run `semiphemeral delete` (this also fetches latest tweets before deleting). The first time it might take a long time. Like with fetching, it will wait when it hits a Twitter rate limit. Let it run once first before automating it.

After you have manually deleted once, you can automatically delete your old tweets by running `semiphemeral delete` once a day in a cron job.

Settings are stored in `~/.semiphemeral/settings.json`. All tweets (including exceptions, and deleted tweets) are stored in a sqlite database `~/.semiphemeral/tweets.db`.

## Development

Make sure you have [pipenv](https://pipenv.readthedocs.io/en/latest/). Then install dependencies:

```sh
pipenv install --dev
```

And run the program like this:

```sh
pipenv run python ./app.py --help
```
