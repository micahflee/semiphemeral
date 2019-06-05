import datetime
import json
from flask import Flask, request, render_template, jsonify, abort, redirect

from .db import Tweet, Thread
from .twitter import Twitter


def create_app(common):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return redirect('/settings')

    @app.route("/settings", methods=['GET', 'POST'])
    def edit_settings():
        common.settings.load()

        if request.method == 'POST':
            common.settings.set('api_key', request.form['api_key'])
            common.settings.set('api_secret', request.form['api_secret'])
            common.settings.set('access_token_key', request.form['access_token_key'])
            common.settings.set('access_token_secret', request.form['access_token_secret'])
            common.settings.set('username', request.form['username'])

            if 'delete_tweets' in request.form:
                common.settings.set('delete_tweets', request.form['delete_tweets'] == 'on')
            else:
                common.settings.set('delete_tweets', False)
            common.settings.set('tweets_days_threshold', int(request.form['tweets_days_threshold']))
            common.settings.set('tweets_retweet_threshold', int(request.form['tweets_retweet_threshold']))
            common.settings.set('tweets_like_threshold', int(request.form['tweets_like_threshold']))
            if 'tweets_threads_threshold' in request.form:
                common.settings.set('tweets_threads_threshold', request.form['tweets_threads_threshold'] == 'on')
            else:
                common.settings.set('tweets_threads_threshold', False)

            if 'retweets_likes' in request.form:
                common.settings.set('retweets_likes', request.form['retweets_likes'] == 'on')
            else:
                common.settings.set('retweets_likes', False)
            if 'retweets_likes_delete_retweets' in request.form:
                common.settings.set('retweets_likes_delete_retweets', request.form['retweets_likes_delete_retweets'] == 'on')
            else:
                common.settings.set('retweets_likes_delete_retweets', False)
            common.settings.set('retweets_likes_retweets_threshold', int(request.form['retweets_likes_retweets_threshold']))
            if 'retweets_likes_delete_likes' in request.form:
                common.settings.set('retweets_likes_delete_likes', request.form['retweets_likes_delete_likes'] == 'on')
            else:
                common.settings.set('retweets_likes_delete_likes', False)
            common.settings.set('retweets_likes_likes_threshold', int(request.form['retweets_likes_likes_threshold']))

            common.settings.save()

            # Recalculate excluded threads with these new settings
            twitter = Twitter(common)
            twitter.calculate_excluded_threads()

        return render_template('settings.html',
            api_key=common.settings.get('api_key'),
            api_secret=common.settings.get('api_secret'),
            access_token_key=common.settings.get('access_token_key'),
            access_token_secret=common.settings.get('access_token_secret'),
            username=common.settings.get('username'),
            delete_tweets=common.settings.get('delete_tweets'),
            tweets_days_threshold=common.settings.get('tweets_days_threshold'),
            tweets_retweet_threshold=common.settings.get('tweets_retweet_threshold'),
            tweets_like_threshold=common.settings.get('tweets_like_threshold'),
            tweets_threads_threshold=common.settings.get('tweets_threads_threshold'),
            retweets_likes=common.settings.get('retweets_likes'),
            retweets_likes_delete_retweets=common.settings.get('retweets_likes_delete_retweets'),
            retweets_likes_retweets_threshold=common.settings.get('retweets_likes_retweets_threshold'),
            retweets_likes_delete_likes=common.settings.get('retweets_likes_delete_likes'),
            retweets_likes_likes_threshold=common.settings.get('retweets_likes_likes_threshold'))

    @app.route("/tweets")
    def tweets():
        return render_template('tweets.html')

    @app.route("/api/statistics")
    def api_statistics():
        return jsonify(common.get_stats())

    @app.route("/api/tweets-to-delete")
    def api_tweets_to_delete():
        """
        This returns a dictionary of status_ids mapped to the text of all tweets that should be deleted
        """
        tweets_to_delete = common.get_tweets_to_delete(include_excluded=True)

        ret = {}
        for tweet in tweets_to_delete:
            if tweet.in_reply_to_status_id:
                is_reply = True
            else:
                is_reply = False

            ret[tweet.status_id] = {
                'text': tweet.text,
                'retweets': tweet.retweet_count,
                'likes': tweet.favorite_count,
                'is_reply': is_reply,
                'excluded': tweet.exclude_from_delete
            }
        return jsonify(ret)

    @app.route("/api/exclude/<int:status_id>/<int:exclude_from_delete>", methods=['POST'])
    def api_exclude(status_id, exclude_from_delete):
        if exclude_from_delete == 1:
            exclude_from_delete = True
        else:
            exclude_from_delete = False

        tweet = common.session.query(Tweet).filter_by(status_id=status_id).first()
        if not tweet:
            abort(400)

        tweet.exclude_from_delete = exclude_from_delete
        common.session.add(tweet)
        common.session.commit()
        return jsonify(True)

    return app
