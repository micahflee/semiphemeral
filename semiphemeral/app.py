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

# Helpers


def _api_validate(expected_fields, json_data):
    for field in expected_fields:
        if field not in json_data:
            return {"valid": False, "message": f"Missing field: {field}"}

        invalid_type = False
        if type(expected_fields[field]) == list:
            if type(json_data[field]) not in expected_fields[field]:
                invalid_type = True
        else:
            if type(json_data[field]) != expected_fields[field]:
                invalid_type = True
        if invalid_type:
            return {
                "valid": False,
                "message": f"Invalid type: {field} should be {expected_fields[field]}, not {type(json_data[field])}",
            }

    return {"valid": True}


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


@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    """
    GET: Respond with user's settings
    POST: Update the settings
    """
    if request.method == "GET":
        has_fetched = settings.get("since_id") != None
        return jsonify(
            {
                "has_fetched": has_fetched,
                "twitter_api_key": settings.get("twitter_api_key"),
                "twitter_api_secret": settings.get("twitter_api_secret"),
                "twitter_access_token": settings.get("twitter_access_token"),
                "twitter_access_token_secret": settings.get(
                    "twitter_access_token_secret"
                ),
                "delete_tweets": settings.get("delete_tweets"),
                "tweets_days_threshold": settings.get("tweets_days_threshold"),
                "tweets_enable_retweet_threshold": settings.get(
                    "tweets_enable_retweet_threshold"
                ),
                "tweets_retweet_threshold": settings.get("tweets_retweet_threshold"),
                "tweets_enable_like_threshold": settings.get(
                    "tweets_enable_like_threshold"
                ),
                "tweets_like_threshold": settings.get("tweets_like_threshold"),
                "tweets_threads_threshold": settings.get("tweets_threads_threshold"),
                "retweets_likes": settings.get("retweets_likes"),
                "retweets_likes_delete_retweets": settings.get(
                    "retweets_likes_delete_retweets"
                ),
                "retweets_likes_retweets_threshold": settings.get(
                    "retweets_likes_retweets_threshold"
                ),
                "retweets_likes_delete_likes": settings.get(
                    "retweets_likes_delete_likes"
                ),
                "retweets_likes_likes_threshold": settings.get(
                    "retweets_likes_likes_threshold"
                ),
                "direct_messages": settings.get("direct_messages"),
                "direct_messages_threshold": settings.get("direct_messages_threshold"),
            }
        )

    elif request.method == "POST":
        try:
            data = json.loads(request.data)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"error": True, "error_message": "Error parsing JSON"})

        # Validate
        valid = _api_validate(
            {
                "delete_tweets": bool,
                "tweets_days_threshold": int,
                "tweets_enable_retweet_threshold": bool,
                "tweets_retweet_threshold": int,
                "tweets_enable_like_threshold": bool,
                "tweets_like_threshold": int,
                "tweets_threads_threshold": bool,
                "retweets_likes": bool,
                "retweets_likes_delete_retweets": bool,
                "retweets_likes_retweets_threshold": int,
                "retweets_likes_delete_likes": bool,
                "retweets_likes_likes_threshold": int,
                "direct_messages": bool,
                "direct_messages_threshold": int,
                "download_all_tweets": bool,
            },
            data,
        )
        if not valid["valid"]:
            return jsonify({"error": True, "error_message": valid["message"]})

        # Update settings
        direct_messages_threshold = int(data["direct_messages_threshold"])
        if direct_messages_threshold > 29:
            direct_messages_threshold = 29

        settings.set("delete_tweets", data["delete_tweets"])
        settings.set("tweets_days_threshold", data["tweets_days_threshold"])
        settings.set(
            "tweets_enable_retweet_threshold", data["tweets_enable_retweet_threshold"]
        )
        settings.set("tweets_retweet_threshold", data["tweets_retweet_threshold"])
        settings.set(
            "tweets_enable_like_threshold", data["tweets_enable_like_threshold"]
        )
        settings.set("tweets_like_threshold", data["tweets_like_threshold"])
        settings.set("tweets_threads_threshold", data["tweets_threads_threshold"])
        settings.set("retweets_likes", data["retweets_likes"])
        settings.set(
            "retweets_likes_delete_retweets", data["retweets_likes_delete_retweets"]
        )
        settings.set(
            "retweets_likes_retweets_threshold",
            data["retweets_likes_retweets_threshold"],
        )
        settings.set("retweets_likes_delete_likes", data["retweets_likes_delete_likes"])
        settings.set(
            "retweets_likes_likes_threshold", data["retweets_likes_likes_threshold"]
        )
        settings.set("direct_messages", data["direct_messages"])
        settings.set("direct_messages_threshold", direct_messages_threshold)

        # Does the user want to force downloading all tweets next time?
        if data["download_all_tweets"]:
            settings.set("since_id", None)

        settings.save()

        # Validate API credentials
        return api_test_creds()


def main():
    print("Use Semiphemeral at: http://localhost:8080/")
    print("Press CTRL-C to quit")
    serve(app, listen="*:8080")


if __name__ == "__main__":
    main()
