import tweepy


# Twitter API v2
def create_tweepy_client_v2(
    consumer_key, consumer_secret, access_token, access_token_secret
):
    return tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        return_type=dict,
        wait_on_rate_limit=True,
    )


# Twitter API v1.1
def create_tweepy_client_v1_1(
    consumer_key, consumer_secret, access_token, access_token_secret
):
    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
    return tweepy.API(auth, wait_on_rate_limit=True)
