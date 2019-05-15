from flask import Flask, request, render_template

from .db import Tweet


def create_app(settings, session):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template('index.html',
            is_configured=settings.is_configured(),
            last_fetch=settings.get('last_fetch'))

    @app.route("/settings", methods=['GET', 'POST'])
    def edit_settings():
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
            is_configured=settings.is_configured(),
            last_fetch=settings.get('last_fetch'),
            api_key=settings.get('api_key'),
            api_secret=settings.get('api_secret'),
            access_token_key=settings.get('access_token_key'),
            access_token_secret=settings.get('access_token_secret'),
            username=settings.get('username'),
            days_threshold=settings.get('days_threshold'),
            retweet_threshold=settings.get('retweet_threshold'),
            like_threshold=settings.get('like_threshold'),
            threads_threshold=settings.get('threads_threshold'),
            exclude_keybase_proof=settings.get('exclude_keybase_proof'))

    @app.route("/exceptions")
    def exceptions():
        return render_template('exceptions.html',
            is_configured=settings.is_configured())

    return app
