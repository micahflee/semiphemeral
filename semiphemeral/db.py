from sqlalchemy import (
    create_engine,
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    job_type = Column(String)  # "download", "delete", "delete_dms", "delete_dm_groups"
    status = Column(
        String, default="pending"
    )  # "pending", "active", "finished", "canceled", "failed"
    progress_status = Column(String, default="")
    progress_tweets_downloaded = Column(Integer, default=0)
    progress_likes_downloaded = Column(Integer, default=0)
    progress_tweets_deleted = Column(Integer, default=0)
    progress_retweets_deleted = Column(Integer, default=0)
    progress_likes_deleted = Column(Integer, default=0)
    progress_dms_deleted = Column(Integer, default=0)
    progress_dms_skipped = Column(Integer, default=0)
    scheduled_timestamp = Column(DateTime)
    started_timestamp = Column(DateTime)
    finished_timestamp = Column(DateTime)

    def __str__(self):
        return f"Job: type={self.job_type}, status={self.status}"

    def to_dict(self):
        if self.scheduled_timestamp:
            scheduled_timestamp = self.scheduled_timestamp.timestamp()
        else:
            scheduled_timestamp = None
        if self.started_timestamp:
            started_timestamp = self.started_timestamp.timestamp()
        else:
            started_timestamp = None
        if self.finished_timestamp:
            finished_timestamp = self.finished_timestamp.timestamp()
        else:
            finished_timestamp = None
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "progress_status": self.progress_status,
            "progress_tweets_downloaded": self.progress_tweets_downloaded,
            "progress_likes_downloaded": self.progress_likes_downloaded,
            "progress_tweets_deleted": self.progress_tweets_deleted,
            "progress_retweets_deleted": self.progress_retweets_deleted,
            "progress_likes_deleted": self.progress_likes_deleted,
            "progress_dms_deleted": self.progress_dms_deleted,
            "progress_dms_skipped": self.progress_dms_skipped,
            "scheduled_timestamp": scheduled_timestamp,
            "started_timestamp": started_timestamp,
            "finished_timestamp": finished_timestamp,
        }


class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String)
    should_exclude = Column(Boolean)

    tweets = relationship("Tweet", back_populates="thread")


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    twitter_id = Column(String)
    created_at = Column(DateTime)
    text = Column(String)
    is_retweet = Column(Boolean)
    retweet_id = Column(String)
    is_reply = Column(Boolean)
    retweet_count = Column(Integer)
    like_count = Column(Integer)
    exclude_from_delete = Column(Boolean)
    is_deleted = Column(Boolean)
    thread_id = Column(Integer, ForeignKey("threads.id"))

    thread = relationship("Thread", back_populates="tweets")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    twitter_id = Column(String)
    created_at = Column(DateTime)
    author_id = Column(String)
    is_deleted = Column(Boolean)


def create_db(database_path):
    engine = create_engine("sqlite:///{}".format(database_path))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return session()
