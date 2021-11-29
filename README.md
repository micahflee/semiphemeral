![Logo](/img/logo-small.png)

# Semiphemeral

There are two different versions of Semiphemeral:

- **[Semiphemeral.com](https://semiphemeral.com/) is a hosted service that's easy for anyone to use**, but does not have all the same features as this open source project.
- **This is the _open source_ version.** It's for advanced users who want total control (non-nerds are better off using semiphemeral.com). It requires using the terminal, generating your own Twitter API key, and if you want to automate it, setting up a server with a cron job. However you don't need to give any access to your Twitter account to a 3rd party (me) and it has more features.

## What is this?

There are plenty of tools that let you make your Twitter feed ephemeral, automatically deleting tweets older than some threshold, like one month.

Semiphemeral does this, but also lets you automatically exclude tweets based on criteria: how many RTs or likes they have, and if they're part of a thread where one of your tweets has that many RTs or likes. It also lets you manually select tweets you'd like to exclude from deleting.

It delete all of your old likes, even really old ones that Twitter makes difficult to delete. And it can automatically delete your old direct messages.

Read more:

* [Semiphemeral: Automatically delete your old tweets, except for the ones you want to keep](https://micahflee.com/2019/06/semiphemeral-automatically-delete-your-old-tweets-except-for-the-ones-you-want-to-keep/)
* [With Semiphemeral you can delete your old Twitter likes, but it's noisy](https://micahflee.com/2019/07/with-semiphemeral-you-can-delete-your-old-twitter-likes-but-its-noisy/)

## Installation

```
pip3 install semiphemeral
```

## How it works

Semiphemeral is a command line tool that you run locally on your computer, or on a server.

```
$ semiphemeral
Usage: -c [OPTIONS] COMMAND [ARGS]...

  Automatically delete your old tweets, except for the ones you want to keep

Options:
  --help  Show this message and exit.

Commands:
  configure        Start the web server to configure semiphemeral
  delete           Delete tweets that aren't automatically or manually
                   excluded, likes, and DMs

  delete_dms       Delete DMs that aren't available through the Twitter API
  excluded_export  Export tweets excluded that are excluded from deletion
  excluded_import  Import tweets excluded that are excluded from deletion
  fetch            Download all tweets/DMs
  stats            Show stats about tweets in the database
  unlike           Delete old likes that aren't available through the Twitter
                   API
```

Start by running `semiphemeral configure`, which starts a local web server at http://127.0.0.1:8080/. Load that website in a browser.

You must supply Twitter API credentials here, which you can get by following [this guide](https://python-twitter.readthedocs.io/en/latest/getting_started.html). Basically, you need to login to https://developer.twitter.com/ and create a new "Twitter app" that only you will be using (when creating an app, you're welcome to use https://github.com/micahflee/semiphemeral as the website URL for your app).

If you want to delete your DMs, you'll have to make sure to give your Twitter app "Read, write, and Direct Messages" permissions, instead of just "Read and write". (If you're modifying an existing app to add Direct Message permissions, you'll have to go to the app's "Keys and tokens" page, and under "Access token & access token secret" click "Regenerate". Then add the new access token key and secret into semiphemeral's settings.)

From the settings page you also tell semiphemeral which tweets to exclude from deletion:

![Settings](/img/settings.png)

Once you have configured semiphemeral, fetch all of the tweets from your account by running `semiphemeral fetch`. (It may take a long time if you have a lot of tweets -- when semiphemeral hits a Twitter rate limit, it just waits the shortest amount of time allowed until it can continue fetching.)

Then go back to the configuration web app and look at the tweets page. From here, you can look at all of the tweets that are going to get deleted the next time you run `semiphemeral delete`, and choose to manually exclude some of them from deletion. This interface paginates all of the tweets that are staged for deletion, and allows you to filter them by searching for phrases in the text of your tweets.

Once you have chosen all tweets you want to exclude, you may want to [download your Twitter archive](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive) for your records.

Then run `semiphemeral delete` (this also fetches latest tweets before deleting). The first time it might take a long time. Like with fetching, it will wait when it hits a Twitter rate limit. Let it run once first before automating it.

After you have manually deleted once, you can automatically delete your old tweets by running `semiphemeral delete` once a day in a cron job.

Settings are stored in `~/.semiphemeral/settings.json`. All tweets (including exceptions, and deleted tweets) are stored in a sqlite database `~/.semiphemeral/tweets.db`.

## Deleting old direct messages

The Twitter API only lets you fetch your last 30 days worth of DMs. If you have years worth of old DMs, you can still delete them all.

This is how to use the `delete_dms` command:

```sh
$ semiphemeral delete_dms --help
Usage: semiphemeral delete_dms [OPTIONS]

Options:
  --filename TEXT  Path to direct-message.js from Twitter data downloaded from
                   https://twitter.com/settings/your_twitter_data  [required]

  --help           Show this message and exit.
```

In order to get a list of all of your DMs (since the Twitter API won't give it to you), you must go to https://twitter.com/settings/your_twitter_data and download your Twitter data (note that this is different than your "Twitter archive", which doesn't include information about your DMs). Twitter will email you a link to a zip file. When you unzip it there will be many files, including a file called `direct-message.js`. Run this command, with the path to your `direct-message.js`, for example:

```sh
semiphemeral delete_dms --filename ~/Downloads/twitter-2020-07-22/direct-message.js
```

Your filename will be different than this one, so make sure you update the command to match it.

This will delete all of your old DMs. New DMs don't have this problem. So as long as you regularly run `semiphemeral delete`, your new DMs will automatically get deleted.

## Deleting old tweets

Semiphemeral deleted about 20,000 of my tweets, starting from my earliest in 2009. But I've heard reports that for some people, Semiphemeral only deletes about 3,000 tweets and can't delete anything earlier.

I don't know why the Twitter API works the way it does, but unfortunately for some users when you say, "hey Twitter, give me a list of all my tweets" it only gives you a list of the most recent 3,000. And if you delete all of those, it gives you a list of 0, even if you have way more.

_At the moment, Semiphemeral can't help you solve this problem._

## Deleting old likes

The Twitter API is only willing to tell you about your last 4000 likes. If you've already tried to fetch and delete your likes, but still have a lot of old likes, you can use semiphemeral to automate unliking them.

_**WARNING: One does not simply unlike old tweets.** Twitter works in mysterious ways. For some reason, even though these old tweets are listed in your like history, the API doesn't believe that you actually liked them. The only way to remove them from your like history is to LIKE THEM AGAIN, and then you can unlike them, and they actually get removed from your like history, and your like count goes down. But this is VERY NOISY. Every time you re-like a tweet, the user will get a notification. If you need to unlike many thousands of old likes, expect messages from friends thinking your Twitter account was hacked or something._

_**WARNING: Prepare to spend WEEKS running this command.** Twitter only allows users to like up to 1000 tweets per day. This means that if you need to unlike 15,000 old tweets, then this script will take 15 days to run! After the first 1000 like/unlikes, the script will pause for 24 hours. If possible, I recommend you run this on a server in a screen or tmux session, so that it doesn't get interrupted when you suspend your laptop. And if you're running semiphemeral on a cron job, I recommend that you disable it first, and then start it up again when it's finished._

This is how to use the `unlike` command:

```sh
$ semiphemeral unlike --help
Usage: semiphemeral unlike [OPTIONS]

Options:
  --filename TEXT  Path to like.js from Twitter data downloaded from
                   https://twitter.com/settings/your_twitter_data  [required]

  --help           Show this message and exit.
```

In order to get a list of all of your old likes (since the Twitter API won't give it to you), you must go to https://twitter.com/settings/your_twitter_data and download your Twitter data (note that this is different than your "Twitter archive", which doesn't include information about your likes). Twitter will email you a link to a zip file. When you unzip it there will be many files, including a file called `like.js`. Run this command, with the path to your `like.js`, for example:

```sh
semiphemeral unlike --filename ~/Downloads/twitter-2020-07-22/like.js
```

Your filename will be different than this one, so make sure you update the command to match it.

This will fetch all of the old tweets you liked a long time ago, and then relike and unlike each one of them. Every relike will cause a notification, but at the end of the process your likes will have actually been deleted. If the command crashes or you cancel in the middle for any reason, it's safe to run it again to continue where you left off.

New likes don't have this problem, so as long as you regularly run `semiphemeral delete`, your new likes will automatically get deleted.

## Development

Make sure you have [pipenv](https://pipenv.readthedocs.io/en/latest/). Then install dependencies:

```sh
pipenv install --dev --pre
```

And run the program like this:

```sh
pipenv run python ./app.py --help
```
