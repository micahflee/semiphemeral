from flask import Flask, request, render_template

from .db import Tweet


def create_app(settings, session):
    app = Flask(__name__)

    def before_each_request():
        settings.load()
        return {
            'is_configured': settings.is_configured(),
            'last_fetch': settings.get('last_fetch')
        }

    @app.route("/")
    def index():
        sidebar = before_each_request()
        return render_template('index.html', sidebar=sidebar)

    @app.route("/settings", methods=['GET', 'POST'])
    def edit_settings():
        sidebar = before_each_request()

        if request.method == 'POST':
            settings.set('api_key', request.form['api_key'])
            settings.set('api_secret', request.form['api_secret'])
            settings.set('access_token_key', request.form['access_token_key'])
            settings.set('access_token_secret', request.form['access_token_secret'])
            settings.set('username', request.form['username'])
            settings.set('days_threshold', int(request.form['days_threshold']))
            settings.set('retweet_threshold', int(request.form['retweet_threshold']))
            settings.set('like_threshold', int(request.form['like_threshold']))
            if 'threads_threshold' in request.form:
                settings.set('threads_threshold', request.form['threads_threshold'] == 'on')
            else:
                settings.set('threads_threshold', False)
            if 'exclude_keybase_proof' in request.form:
                settings.set('exclude_keybase_proof', request.form['exclude_keybase_proof'] == 'on')
            else:
                settings.set('exclude_keybase_proof', False)
            settings.save()

        return render_template('settings.html',
            sidebar=sidebar,
            api_key=settings.get('api_key'),
            api_secret=settings.get('api_secret'),
            access_token_key=settings.get('access_token_key'),
            access_token_secret=settings.get('access_token_secret'),
            username=settings.get('username'),
            days_threshold=settings.get('days_threshold'),
            retweet_threshold=settings.get('retweet_threshold'),
            like_threshold=settings.get('like_threshold'),
            threads_threshold=settings.get('threads_threshold'))

    @app.route("/tweets")
    def tweets():
        sidebar = before_each_request()

        # Statistics
        my_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=0 AND is_retweet=0'.format(int(settings.get('user_id')))).first()[0]
        my_retweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=0 AND is_retweet=1'.format(int(settings.get('user_id')))).first()[0]
        deleted_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=0'.format(int(settings.get('user_id')))).first()[0]
        deleted_retweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND is_deleted=1 AND is_retweet=1'.format(int(settings.get('user_id')))).first()[0]
        excluded_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id={} AND exclude_from_delete=1'.format(int(settings.get('user_id')))).first()[0]
        other_tweets = session.execute('SELECT COUNT(*) FROM tweets WHERE user_id!={}'.format(int(settings.get('user_id')))).first()[0]
        threads = session.execute('SELECT COUNT(*) FROM threads').first()[0]

        return render_template('tweets.html',
            sidebar=sidebar,
            my_tweets=my_tweets,
            my_retweets=my_retweets,
            deleted_tweets=deleted_tweets,
            deleted_retweets=deleted_retweets,
            excluded_tweets=excluded_tweets,
            other_tweets=other_tweets,
            threads=threads)

    return app
