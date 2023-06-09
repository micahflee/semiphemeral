#!/usr/bin/env python3
import os

from waitress import serve
from flask import Flask, send_from_directory

from .settings import Settings
from .db import create_db


# Initialize settings and database
base = os.path.expanduser("~/.semiphemeral")
os.makedirs(base, mode=0o700, exist_ok=True)
settings = Settings(os.path.join(base, "settings.json"))
session = create_db(os.path.join(base, "data.db"))

# Initialize Flask
app = Flask(__name__)

# Static assets


@app.route("/assets/<path:filename>")
def static_assets(filename):
    return send_from_directory(f"frontend/dist/assets", filename)


@app.route("/images/<path:filename>")
def static_images(filename):
    return send_from_directory(f"frontend/dist/images", filename)


# Frontend routes


@app.route("/")
@app.route("/tweets")
@app.route("/export")
@app.route("/dms")
@app.route("/settings")
@app.route("/faq")
def web_frontend():
    with open(f"frontend/dist/index.html") as f:
        body = f.read()

    return body


# API routes


@app.route("/api/user")
def api_user():
    """
    Respond with information about the Twitter user
    """
    pass


def main():
    print("Use Semiphemeral at: http://localhost:8080/")
    print("Press CTRL-C to quit")
    serve(app, listen="*:8080")


if __name__ == "__main__":
    main()
