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
            'days_threshold': 30,
            'retweet_threshold': 100,
            'like_threshold': 100,
            'threads_threshold': True,
            'exclude_keybase_proof': True,
            'since_id': None,
            'last_fetch': None
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

    def is_configured(self):
        if self.get('api_key') == '' or \
            self.get('api_secret') == '' or \
            self.get('access_token_key') == '' or \
            self.get('access_token_secret') == '' or \
            self.get('username') == '':
            return False
        return True
