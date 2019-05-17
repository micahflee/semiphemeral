from flask import Flask, request, render_template, jsonify

from .db import Tweet


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
            if 'tweets_delete_retweets' in request.form:
                settings.set('tweets_delete_retweets', request.form['tweets_delete_retweets'] == 'on')
            else:
                settings.set('tweets_delete_retweets', False)
            settings.save()

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
            tweets_delete_retweets=settings.get('tweets_delete_retweets'))

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
        deleted_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=0'.format(int(settings.get('user_id')))).first()[0]
        deleted_retweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=1'.format(int(settings.get('user_id')))).first()[0]
        excluded_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND exclude_from_delete=1'.format(int(settings.get('user_id')))).first()[0]
        other_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id!={}'.format(int(settings.get('user_id')))).first()[0]
        threads = session.execute('SELECT COUNT(*) FROM threads').first()[0]

        return jsonify({
            'is_configured': is_configured,
            'last_fetch': last_fetch,
            'my_tweets': my_tweets,
            'my_retweets': my_retweets,
            'deleted_tweets': deleted_tweets,
            'deleted_retweets': deleted_retweets,
            'excluded_tweets': excluded_tweets,
            'other_tweets': other_tweets,
            'threads': threads
        })


    return app
