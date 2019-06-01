import datetime
import json
from flask import Flask, request, render_template, jsonify, abort

from .db import Tweet, Thread
from .twitter import Twitter


def create_app(settings, session):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/settings", methods=['GET', 'POST'])
    def edit_settings():
        settings.load()

        if request.method == 'POST':
            settings.set('api_key', request.form['api_key'])
            settings.set('api_secret', request.form['api_secret'])
            settings.set('access_token_key', request.form['access_token_key'])
            settings.set('access_token_secret', request.form['access_token_secret'])
            settings.set('username', request.form['username'])

            if 'delete_tweets' in request.form:
                settings.set('delete_tweets', request.form['delete_tweets'] == 'on')
            else:
                settings.set('delete_tweets', False)
            settings.set('tweets_days_threshold', int(request.form['tweets_days_threshold']))
            settings.set('tweets_retweet_threshold', int(request.form['tweets_retweet_threshold']))
            settings.set('tweets_like_threshold', int(request.form['tweets_like_threshold']))
            if 'tweets_threads_threshold' in request.form:
                settings.set('tweets_threads_threshold', request.form['tweets_threads_threshold'] == 'on')
            else:
                settings.set('tweets_threads_threshold', False)

            if 'retweets_likes' in request.form:
                settings.set('retweets_likes', request.form['retweets_likes'] == 'on')
            else:
                settings.set('retweets_likes', False)
            if 'retweets_likes_delete_retweets' in request.form:
                settings.set('retweets_likes_delete_retweets', request.form['retweets_likes_delete_retweets'] == 'on')
            else:
                settings.set('retweets_likes_delete_retweets', False)
            settings.set('retweets_likes_retweets_threshold', int(request.form['retweets_likes_retweets_threshold']))
            if 'retweets_likes_delete_likes' in request.form:
                settings.set('retweets_likes_delete_likes', request.form['retweets_likes_delete_likes'] == 'on')
            else:
                settings.set('retweets_likes_delete_likes', False)
            settings.set('retweets_likes_likes_threshold', int(request.form['retweets_likes_likes_threshold']))

            settings.save()

            # Recalculate excluded threads with these new settings
            twitter = Twitter(settings, session)
            twitter.calculate_excluded_threads()

        return render_template('settings.html',
            api_key=settings.get('api_key'),
            api_secret=settings.get('api_secret'),
            access_token_key=settings.get('access_token_key'),
            access_token_secret=settings.get('access_token_secret'),
            username=settings.get('username'),
            delete_tweets=settings.get('delete_tweets'),
            tweets_days_threshold=settings.get('tweets_days_threshold'),
            tweets_retweet_threshold=settings.get('tweets_retweet_threshold'),
            tweets_like_threshold=settings.get('tweets_like_threshold'),
            tweets_threads_threshold=settings.get('tweets_threads_threshold'),
            retweets_likes=settings.get('retweets_likes'),
            retweets_likes_delete_retweets=settings.get('retweets_likes_delete_retweets'),
            retweets_likes_retweets_threshold=settings.get('retweets_likes_retweets_threshold'),
            retweets_likes_delete_likes=settings.get('retweets_likes_delete_likes'),
            retweets_likes_likes_threshold=settings.get('retweets_likes_likes_threshold'))

    @app.route("/tweets")
    def tweets():
        return render_template('tweets.html')

    @app.route("/api/statistics")
    def api_statistics():
        settings.load()

        is_configured = settings.is_configured()
        last_fetch = settings.get('last_fetch')
        my_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=0 AND is_retweet=0'.format(int(settings.get('user_id')))).first()[0]
        my_retweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=0 AND is_retweet=1'.format(int(settings.get('user_id')))).first()[0]
        my_likes = session.execute('SELECT COUNT(*) FROM tweets WHERE favorited=1').first()[0]
        deleted_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=0'.format(int(settings.get('user_id')))).first()[0]
        deleted_retweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=1'.format(int(settings.get('user_id')))).first()[0]
        unliked_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE favorited=1 AND is_unliked=1').first()[0]
        excluded_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND exclude_from_delete=1'.format(int(settings.get('user_id')))).first()[0]
        other_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id!={}'.format(int(settings.get('user_id')))).first()[0]
        threads = session.execute('SELECT COUNT(*) FROM threads').first()[0]

        return jsonify({
            'is_configured': is_configured,
            'last_fetch': last_fetch,
            'my_tweets': my_tweets,
            'my_retweets': my_retweets,
            'my_likes': my_likes,
            'deleted_tweets': deleted_tweets,
            'deleted_retweets': deleted_retweets,
            'unliked_tweets': unliked_tweets,
            'excluded_tweets': excluded_tweets,
            'other_tweets': other_tweets,
            'threads': threads
        })

    @app.route("/api/tweets-to-delete")
    def api_tweets_to_delete():
        """
        This returns a dictionary of status_ids mapped to the text of all tweets that should be deleted
        """
        settings.load()
        datetime_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=settings.get('tweets_days_threshold'))

        # Select tweets from threads to exclude
        tweets_to_exclude = []
        threads = session.query(Thread) \
            .filter(Thread.should_exclude == True) \
            .all()
        for thread in threads:
            for tweet in thread.tweets:
                if tweet.user_id == settings.get('user_id'):
                    tweets_to_exclude.append(tweet.status_id)

        # Select tweets that we will delete
        tweets_to_delete = {}
        tweets = session.query(Tweet) \
            .filter(Tweet.user_id == int(settings.get('user_id'))) \
            .filter(Tweet.is_deleted == 0) \
            .filter(Tweet.is_retweet == 0) \
            .filter(Tweet.created_at < datetime_threshold) \
            .filter(Tweet.retweet_count < settings.get('tweets_retweet_threshold')) \
            .filter(Tweet.favorite_count < settings.get('tweets_like_threshold')) \
            .all()
        for tweet in tweets:
            if tweet.status_id not in tweets_to_exclude:
                tweets_to_delete[tweet.status_id] = {
                    'text': tweet.text,
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count,
                    'excluded': tweet.exclude_from_delete
                }

        return jsonify(tweets_to_delete)

    @app.route("/api/exclude/<int:status_id>/<int:exclude_from_delete>", methods=['POST'])
    def api_exclude(status_id, exclude_from_delete):
        if exclude_from_delete == 1:
            exclude_from_delete = True
        else:
            exclude_from_delete = False

        tweet = session.query(Tweet).filter_by(status_id=status_id).first()
        if not tweet:
            abort(400)

        tweet.exclude_from_delete = exclude_from_delete
        session.add(tweet)
        session.commit()
        return jsonify(True)

    return app
