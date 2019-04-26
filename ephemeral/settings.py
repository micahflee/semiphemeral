import os
import json


class Settings(object):
    def __init__(self, filename):
        self.filename = filename
        self.default_settings = {
            'api_key': '',
            'api_secret': '',
            'access_token_key': '',
            'access_token_secret': '',
            'username': '',
            'exclude_newer_than_n_days': 30,
            'exclude_retweet_threshold': 100,
            'exclude_like_threshold': 100,
            'exclude_threads_threshold': True,
            'exclude_keybase_proof': True
        }
        self.load()

    def get(self, key):
        return self.settings[key]

    def set(self, key, val):
        self.settings[key] = val

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.settings = json.load(f)

            for key in self.default_settings:
                if key not in self.settings:
                    self.set(key, self.default_settings[key])
        else:
            self.settings = self.default_settings.copy()

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.settings, f)
