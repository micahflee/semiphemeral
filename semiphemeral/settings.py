import os
import json


class Settings(object):
    def __init__(self, filename):
        self.filename = filename
        self.default_settings = {
            "twitter_id": "",
            "twitter_screen_name": "",
            "profile_image_url_https": "",
            "twitter_api_key": "",
            "twitter_api_secret": "",
            "twitter_access_token": "",
            "twitter_access_token_secret": "",
            "delete_tweets": False,
            "tweets_days_threshold": 30,
            "tweets_enable_retweet_threshold": True,
            "tweets_retweet_threshold": 20,
            "tweets_enable_like_threshold": True,
            "tweets_like_threshold": 20,
            "tweets_threads_threshold": True,
            "retweets_likes": False,
            "retweets_likes_delete_retweets": True,
            "retweets_likes_retweets_threshold": 30,
            "retweets_likes_delete_likes": True,
            "retweets_likes_likes_threshold": 60,
            "direct_messages": False,
            "direct_messages_threshold": 7,
            "since_id": None,
            "last_fetch": None,
        }
        self.load()

    def get(self, key):
        return self.settings[key]

    def set(self, key, val):
        self.settings[key] = val

    def get_all(self):
        return self.settings.copy()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.settings = json.load(f)

            for key in self.default_settings:
                if key not in self.settings:
                    self.set(key, self.default_settings[key])
        else:
            self.settings = self.default_settings.copy()

    def save(self):
        with open(self.filename, "w") as f:
            os.chmod(self.filename, 0o0600)
            json.dump(self.settings, f, indent=2, sort_keys=True)

    def is_configured(self):
        if (
            self.get("twitter_api_key") == ""
            or self.get("twitter_api_secret") == ""
            or self.get("twitter_access_token") == ""
            or self.get("twitter_access_token_secret") == ""
            or self.get("twitter_screen_name") == ""
        ):
            return False
        return True
