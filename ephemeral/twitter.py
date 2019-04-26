import twitter


class Twitter(object):
    def __init__(self, settings, session):
        self.settings = settings
        self.session = session

        self.authenticated = False

        if not self.settings.is_configured():
            print('Twitter API is not configured yet, configure it with --configure')
            return

        self.api = twitter.Api(consumer_key=self.settings.get('api_key'),
            consumer_secret=self.settings.get('api_secret'),
            access_token_key=self.settings.get('access_token_key'),
            access_token_secret=self.settings.get('access_token_secret'))
        self.authenticated = True

        self.user = self.api.GetUser(screen_name=self.settings.get('username'))

    def fetch(self):
        if not self.authenticated:
            return

        print('Not implemented yet')

    def delete(self):
        if not self.authenticated:
            return

        print('Not implemented yet')
