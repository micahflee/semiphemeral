#!/usr/bin/env python3
import os
import json

from waitress import serve
from flask import Flask, send_from_directory, jsonify, request

from .settings import Settings
from .db import create_db
from .common import create_tweepy_client_v1_1


# Initialize settings and database
base = os.path.expanduser("~/.semiphemeral")
os.makedirs(base, mode=0o700, exist_ok=True)
settings = Settings(os.path.join(base, "settings.json"))
session = create_db(os.path.join(base, "data.db"))

# Initialize Flask
app = Flask(__name__)

# Static assets

dist_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend/dist")


@app.route("/assets/<path:filename>")
def static_assets(filename):
    return send_from_directory(os.path.join(dist_path, "assets"), filename)


@app.route("/images/<path:filename>")
def static_images(filename):
    return send_from_directory(os.path.join(dist_path, "images"), filename)


# Frontend routes


@app.route("/")
@app.route("/tweets")
@app.route("/export")
@app.route("/dms")
@app.route("/settings")
@app.route("/faq")
def web_frontend():
    return send_from_directory(dist_path, "index.html")


# API routes


@app.route("/api/user")
def api_user():
    """
    Respond with information about the Twitter user
    """
    if settings.is_configured():
        return jsonify(
            {
                "is_configured": True,
                "user_screen_name": settings.get("twitter_screen_name"),
                "user_profile_url": settings.get("profile_image_url_https"),
            }
        )
    else:
        return jsonify({"is_configured": False})


@app.route("/api/test-creds", methods=["POST"])
def api_test_creds():
    """
    Test if given API credentials work, and if so update the settings
    """
    try:
        data = json.loads(request.data)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return jsonify({"error": True, "error_message": "Error parsing JSON"})

    # Validate that data contains twitter_api_key, twitter_api_secret, twitter_access_token, and twitter_access_token_secret
    for key in [
        "twitter_api_key",
        "twitter_api_secret",
        "twitter_access_token",
        "twitter_access_token_secret",
    ]:
        if key not in data or data[key].strip() == "":
            return jsonify({"error": True, "error_message": f"Missing {key}"})

    # Test the API credentials
    api = create_tweepy_client_v1_1(
        data["twitter_api_key"],
        data["twitter_api_secret"],
        data["twitter_access_token"],
        data["twitter_access_token_secret"],
    )
    try:
        response = api.verify_credentials()
    except Exception as e:
        print(f"Error verifying credentials: {e}")
        return jsonify(
            {"error": True, "error_message": f"Error verifying credentials: {e}"}
        )

    # Update the settings
    settings.set("twitter_api_key", data["twitter_api_key"])
    settings.set("twitter_api_secret", data["twitter_api_secret"])
    settings.set("twitter_access_token", data["twitter_access_token"])
    settings.set("twitter_access_token_secret", data["twitter_access_token_secret"])
    settings.set("twitter_id", response.id_str)
    settings.set("twitter_screen_name", response.screen_name)
    settings.set("profile_image_url_https", response.profile_image_url_https)
    settings.save()

    return jsonify({"error": False})


def main():
    print("Use Semiphemeral at: http://localhost:8080/")
    print("Press CTRL-C to quit")
    serve(app, listen="*:8080")


if __name__ == "__main__":
    main()
