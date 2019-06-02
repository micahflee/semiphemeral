import click

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True)
    root_status_id = Column(Integer)
    should_exclude = Column(Boolean)

    tweets = relationship("Tweet", back_populates="thread")

    def __init__(self, root_status_id):
        self.root_status_id = root_status_id
        self.should_exclude = False


class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    user_id = Column(Integer) # we download all threads too, including with other users
    user_screen_name = Column(String)
    status_id = Column(Integer)
    lang = Column(String)
    source = Column(String)
    source_url = Column(String)
    text = Column(String)
    in_reply_to_screen_name = Column(String)
    in_reply_to_status_id = Column(Integer)
    in_reply_to_user_id = Column(Integer)
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)
    retweeted = Column(Boolean)
    favorited = Column(Boolean)
    is_retweet = Column(Boolean)
    is_deleted = Column(Boolean)
    is_unliked = Column(Boolean)
    exclude_from_delete = Column(Boolean)

    thread_id = Column(Integer, ForeignKey('threads.id'))
    thread = relationship("Thread", back_populates="tweets")

    def __init__(self, status):
        self.created_at = status.created_at
        self.user_id = status.author.id
        self.user_screen_name = status.author.screen_name
        self.status_id = status.id
        self.lang = status.lang
        self.source = status.source
        self.source_url = status.source_url
        self.text = status.text
        self.in_reply_to_screen_name = status.in_reply_to_screen_name
        self.in_reply_to_status_id = status.in_reply_to_status_id
        self.in_reply_to_user_id = status.in_reply_to_user_id
        self.retweet_count = status.retweet_count
        self.favorite_count = status.favorite_count
        self.retweeted = status.retweeted
        self.favorited = status.favorited
        self.is_retweet = hasattr(status, 'retweeted_status')
        self.is_deleted = False
        self.is_unliked = False
        self.exclude_from_delete = False

    def already_saved(self, session):
        """
        Returns true if a tweet with this status_id is already in the db
        """
        tweet = session.query(Tweet).filter_by(status_id=self.status_id).first()
        if tweet:
            click.secho('Skipped {} @{}, id={}'.format(
                self.created_at.strftime('%Y-%m-%d'),
                self.user_screen_name,
                self.status_id), dim=True)
            return True

    def fetch_summarize(self):
        click.echo('Fetched {}'.format(self.summarize_string()))

    def unretweet_summarize(self):
        click.echo('Unretweeted {}'.format(self.summarize_string(True)))

    def unlike_summarize(self):
        click.echo('Unliked {}'.format(self.summarize_string()))

    def delete_summarize(self):
        click.echo('Deleted {}'.format(self.summarize_string()))

    def summarize_string(self, include_rt_user=False):
        if include_rt_user:
            return '{} @{} {}, id={}'.format(
                self.created_at.strftime('%Y-%m-%d'),
                self.user_screen_name,
                self.text.split(':')[0],
                self.status_id)
        else:
            return '{} @{}, id={}'.format(
                self.created_at.strftime('%Y-%m-%d'),
                self.user_screen_name,
                self.status_id)

def create_db(database_path):
    engine = create_engine('sqlite:///{}'.format(database_path))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return session()
