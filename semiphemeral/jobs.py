import time
from datetime import datetime, timedelta

from sqlalchemy import select, update, or_
from sqlalchemy.sql import text
import tweepy

from .common import create_tweepy_client_v1_1
from .db import Job, Thread, Tweet, Like

# Helpers

def start_job(socketio, db_session, job, progress_status):
    job.status = "active"
    job.progress_status = progress_status
    job.started_timestamp = datetime.now()
    db_session.add(job)
    db_session.commit()
    socketio.emit("update")

def fail_job(socketio, db_session, job, progress_status):
    job.status = "failed"
    job.progress_status = progress_status
    job.finished_timestamp = datetime.now()
    db_session.add(job)
    db_session.commit()
    socketio.emit("update")

def cancel_job(socketio, db_session, job, progress_status):
    job.status = "canceled"
    job.progress_status = progress_status
    job.finished_timestamp = datetime.now()
    db_session.add(job)
    db_session.commit()
    socketio.emit("update")

def finish_job(socketio, db_session, job, progress_status):
    job.status = "finished"
    job.progress_status = progress_status
    job.finished_timestamp = datetime.now()
    db_session.add(job)
    db_session.commit()
    socketio.emit("update")

def update_progress(socketio, db_session, job, progress_status=None):
    if progress_status:
        job.progress_status = progress_status
    db_session.add(job)
    db_session.commit()
    socketio.emit("progress", job.to_dict())

def handle_tweepy_exception(e, api_endpoint):
    print(f"Error on {api_endpoint}, sleeping 60s: {e}")
    time.sleep(60)

# Job running loop
def run_jobs(socketio, db_session, settings):
    while True:
        pending_jobs = db_session.scalars(
            select(Job).where(Job.status == "pending").order_by(Job.scheduled_timestamp)
        ).fetchall()

        for job in pending_jobs:
            if job.job_type == "download":
                download(socketio, db_session, settings, job)
            elif job.job_type == "delete":
                print("Job type 'delete' not implemented yet")
            elif job.job_type == "delete_dms":
                print("Job type 'delete_dms' not implemented yet")
            elif job.job_type == "delete_dm_groups":
                print("Job type 'delete_dm_groups' not implemented yet")
            else:
                print(f"Unknown job type: {job.job_type}, failing job")
                fail_job(socketio, db_session, job, f"Unkown job type: {job.job_type}")

        time.sleep(1)

# Download job
def download(socketio, db_session, settings, job):
    print(f"Starting download job: {job}")
    start_job(socketio, db_session, job, "Download started")

    # Create Twitter API client
    api = create_tweepy_client_v1_1(
        settings.get("twitter_api_key"),
        settings.get("twitter_api_secret"),
        settings.get("twitter_access_token"),
        settings.get("twitter_access_token_secret"),
    )
    try:
        response = api.verify_credentials()
    except Exception as e:
        fail_job(socketio, db_session, job, f"Failed to verify credentials: {e}")
        socketio.emit("fail", {"message": f"Failed to verify credentials: {e}"})
        return

    since_id = settings.get("since_id")

    print("Download started")

    # Start the data
    if since_id:
        update_progress(socketio, db_session, job, "Downloading recent tweets")
    else:
        update_progress(socketio, db_session, job, "Downloading all tweets, this first run may take a long time")

    # In API v1.1 we don't get conversation_id, so we have to make a zillion requests to figure it out ourselves.
    # This dict helps to cache that so we can avoid requests. Each item is a tuple (id, in_reply_to_id)
    cache = {}

    # Fetch tweets
    while True:
        try:
            for page in tweepy.Cursor(
                api.user_timeline, user_id=settings.get("twitter_id"), count=200, since_id=since_id
            ).pages():
                print(f"Importing {len(page)} tweets")
                for status in page:
                    # Get the conversation_id of this tweet
                    conversation_id = status.id_str
                    if status.in_reply_to_status_id_str is not None:
                        in_reply_to_id = status.in_reply_to_status_id_str
                        while True:
                            if in_reply_to_id in cache:
                                _id, _in_reply_to_id = cache[in_reply_to_id]
                            else:
                                try:
                                    response = api.get_status(in_reply_to_id)
                                    _id = response.id_str
                                    _in_reply_to_id = response.in_reply_to_status_id_str
                                    cache[in_reply_to_id] = (_id, _in_reply_to_id)
                                except:
                                    break

                            if _in_reply_to_id is None:
                                conversation_id = _id
                                break
                            else:
                                conversation_id = _id
                                in_reply_to_id = _in_reply_to_id

                    # Make sure we have a thread for this tweet
                    thread = db_session.scalar(
                        select(Thread)
                        .where(Thread.conversation_id == conversation_id)
                    )
                    if not thread:
                        thread = Thread(
                            conversation_id=conversation_id,
                            should_exclude=False,
                        )
                        db_session.add(thread)
                        db_session.commit()

                    # Save or update the tweet
                    tweet = db_session.scalar(
                        select(Tweet)
                        .where(Tweet.twitter_id == status.id_str)
                    )

                    is_retweet = hasattr(status, "retweeted_status")
                    if is_retweet:
                        retweet_id = status.retweeted_status.id_str
                    else:
                        retweet_id = None

                    is_reply = status.in_reply_to_status_id_str is not None

                    if not tweet:
                        tweet = Tweet(
                            twitter_id=status.id_str,
                            created_at=status.created_at.replace(tzinfo=None),
                            text=status.text,
                            is_retweet=is_retweet,
                            retweet_id=retweet_id,
                            is_reply=is_reply,
                            retweet_count=status.retweet_count,
                            like_count=status.favorite_count,
                            exclude_from_delete=False,
                            is_deleted=False,
                            thread_id=thread.id,
                        )
                    else:
                        tweet.text = status.text
                        tweet.is_retweet = is_retweet
                        tweet.retweet_id = retweet_id
                        tweet.is_reply = is_reply
                        tweet.retweet_count = status.retweet_count
                        tweet.like_count = status.favorite_count
                        tweet.thread_id = thread.id

                    db_session.add(tweet)

                    job.progress_tweets_downloaded += 1

                update_progress(socketio, db_session, job)
            break
        except tweepy.errors.Forbidden as e:
            print(f"Forbidden error, pausing user and canceling job: {e}")
            fail_job(socketio, db_session, job, f"Forbidden error, pausing user: {e}")
            return
        except tweepy.errors.TwitterServerError as e:
            update_progress(socketio, db_session, job, "Twitter server error, retrying in 60 seconds")
            handle_tweepy_exception(e, "api.user_timeline")

    # Update progress
    if since_id:
        update_progress(socketio, db_session, job, "Downloading recent likes")
    else:
        update_progress(socketio, db_session, job, "Downloading all likes, this first run may take a long time")

    # Fetch likes
    while True:
        try:
            for page in tweepy.Cursor(
                api.get_favorites, user_id=settings.get("twitter_id"), count=200, since_id=since_id
            ).pages():
                print(f"Importing {len(page)} likes")
                for status in page:
                    # Is the like already saved?
                    like = db_session.scalar(
                        select(Like)
                        .where(Like.twitter_id == status.id_str)
                    )
                    if not like:
                        # Save the like
                        like = Like(
                            twitter_id=status.id_str,
                            created_at=status.created_at.replace(tzinfo=None),
                            author_id=status.user.id_str,
                            is_deleted=False,
                        )
                        db_session.add(like)

                    job.progress_likes_downloaded += 1

                update_progress(socketio, db_session, job)

            break
        except tweepy.errors.Forbidden as e:
            print(f"Forbidden error, pausing user and canceling job: {e}")
            fail_job(socketio, db_session, job, f"Forbidden error, pausing user: {e}")
            return
        except tweepy.errors.TwitterServerError as e:
            update_progress(socketio, db_session, job, "Twitter server error, retrying in 60 seconds")
            handle_tweepy_exception(e, "api.get_favorites")

    # All done, update the since_id
    with db_session.begin() as conn:
        new_since_id = conn.execute(
            text(
                "SELECT twitter_id FROM tweets ORDER BY CAST(twitter_id AS bigint) DESC LIMIT 1",
            )
        ).scalar()

    settings.set("since_id", new_since_id)
    settings.save()

    # Based on the user's settings, figure out which threads should be excluded from deletion,
    # and which threads should have their tweets deleted

    # Calculate which threads should be excluded from deletion
    update_progress(socketio, db_session, job, "Calculating which threads to exclude from deletion")

    # Reset the should_exclude flag for all threads
    db_session.execute(
        update(Thread)
        .values({"should_exclude": False})
    )

    # Set should_exclude for all threads based on the settings
    if settings.get("tweets_threads_threshold"):
        threads = db_session.scalars(
            select(Thread)
            .join(Thread.tweets)
            .where(Thread.id == Tweet.thread_id)
            .where(Tweet.is_deleted == False)
            .where(Tweet.is_retweet == False)
            .where(Tweet.retweet_count >= settings.get("tweets_retweet_threshold"))
            .where(Tweet.like_count >= settings.get("tweets_like_threshold"))
        ).fetchall()
        for thread in threads:
            thread.should_exclude = True
            db_session.add(thread)

        db_session.commit()

    finish_job(socketio, db_session, job, "Finished")

    print("Download finished")
