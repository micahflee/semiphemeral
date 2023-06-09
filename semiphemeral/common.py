from datetime import datetime, timedelta

import tweepy
from sqlalchemy import select

from .db import Job


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


# Add a job
def add_job(db_session, job_type):
    scheduled_timestamp = datetime.now()

    # Make sure there's not already a scheduled job of this type
    existing_job = db_session.scalar(
        select(Job).where(Job.job_type == job_type).where(Job.status == "pending")
    )
    if existing_job:
        print(
            f"Skipping adding {job_type} job, job is already pending",
        )
        return

    # Add the job
    job = Job(
        job_type=job_type,
        scheduled_timestamp=scheduled_timestamp,
    )
    db_session.add(job)
    db_session.commit()
