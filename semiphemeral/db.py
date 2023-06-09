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
    )  # "pending", "active", "finished", "canceled"
    progress_status = Column(String, default="")
    progress_tweets_downloaded = Column(Integer, default=0)
    progress_likes_downloaded = Column(Integer, default=0)
    progress_tweets_deleted = Column(Integer, default=0)
    progress_retweets_deleted = Column(Integer, default=0)
    progress_likes_deleted = Column(Integer, default=0)
    progress_dms_deleted = Column(Integer, default=0)
    scheduled_timestamp = Column(DateTime)
    started_timestamp = Column(DateTime)
    finished_timestamp = Column(DateTime)

    def __str__(self):
        return f"Job: type={self.job_type}, status={self.status}, data={self.data}"


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
    is_fascist = Column(Boolean)


def create_db(database_path):
    engine = create_engine("sqlite:///{}".format(database_path))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return session()
