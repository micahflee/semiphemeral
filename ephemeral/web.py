from flask import Flask, render_template

from .db import Tweet


def create_app(settings, session):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/settings")
    def settings():
        return render_template('settings.html')

    @app.route("/exceptions")
    def exceptions():
        return render_template('exceptions.html')

    return app
