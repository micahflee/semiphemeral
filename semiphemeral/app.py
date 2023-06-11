#!/usr/bin/env python3
import os
import json

from waitress import serve
from flask import Flask, send_from_directory, jsonify, request
from sqlalchemy import select

from .settings import Settings
from .db import create_db, Job
from .common import create_tweepy_client_v1_1, add_job

# Initialize settings and database
base = os.path.expanduser("~/.semiphemeral")
os.makedirs(base, mode=0o700, exist_ok=True)
settings = Settings(os.path.join(base, "settings.json"))
db_session = create_db(os.path.join(base, "data.db"))

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


@app.route("/api/dashboard", methods=["GET", "POST"])
def api_dashboard():
    """
    GET: Respond with the lists of active, pending, and finished jobs
    POST: Download or delete twitter data
    """
    if request.method == "GET":
        pending_jobs = db_session.scalars(
            select(Job).where(Job.status == "pending").order_by(Job.scheduled_timestamp)
        ).fetchall()
        active_jobs = db_session.scalars(
            select(Job).where(Job.status == "active").order_by(Job.started_timestamp)
        ).fetchall()
        finished_jobs = db_session.scalars(
            select(Job)
            .where(Job.status == "finished")
            .order_by(Job.finished_timestamp.desc())
        ).fetchall()

        def to_client(jobs):
            jobs_json = []
            for job in jobs:
                if job.scheduled_timestamp:
                    scheduled_timestamp = job.scheduled_timestamp.timestamp()
                else:
                    scheduled_timestamp = None
                if job.started_timestamp:
                    started_timestamp = job.started_timestamp.timestamp()
                else:
                    started_timestamp = None
                if job.finished_timestamp:
                    finished_timestamp = job.finished_timestamp.timestamp()
                else:
                    finished_timestamp = None

                jobs_json.append(
                    {
                        "id": job.id,
                        "job_type": job.job_type,
                        "status": job.status,
                        "progress_status": job.progress_status,
                        "progress_tweets_downloaded": job.progress_tweets_downloaded,
                        "progress_likes_downloaded": job.progress_likes_downloaded,
                        "progress_tweets_deleted": job.progress_tweets_deleted,
                        "progress_retweets_deleted": job.progress_retweets_deleted,
                        "progress_likes_deleted": job.progress_likes_deleted,
                        "progress_dms_deleted": job.progress_dms_deleted,
                        "scheduled_timestamp": scheduled_timestamp,
                        "started_timestamp": started_timestamp,
                        "finished_timestamp": finished_timestamp,
                    }
                )
            return jobs_json

        return jsonify(
            {
                "pending_jobs": to_client(pending_jobs),
                "active_jobs": to_client(active_jobs),
                "finished_jobs": to_client(finished_jobs),
            }
        )

    elif request.method == "POST":
        """
        If action is download, create a download job
        If action is delete, create a delete job
        """
        try:
            data = json.loads(request.data)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"error": True, "error_message": "Error parsing JSON"})

        # Validate
        valid = _api_validate({"action": str}, data)
        if not valid["valid"]:
            return jsonify({"error": True, "error_message": valid["message"]})

        if data["action"] != "download" and data["action"] != "delete":
            return jsonify(
                {
                    "error": True,
                    "error_message": "Action must be 'download' or 'delete'",
                }
            )

        if data["action"] == "download":
            add_job("download")

        elif data["action"] == "delete":
            add_job("delete")

        return jsonify(True)

    else:
        return jsonify({"error": True, "error_message": "Bad request"})


@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    """
    GET: Respond with user's settings
    POST: Update the settings
    """
    if request.method == "GET":
        return jsonify(
            {
                "is_configured": True,
                "settings": settings.get_all()
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
