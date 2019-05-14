import click

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


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
    exclude_from_delete = Column(Boolean)

    def __init__(self, status):
        self.created_at = status.created_at
        self.user_id = status.author.id
        self.user_screen_name = status.author.screen_name
        self.status_id = status.id
        self.lang =status.lang
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

    def summarize(self):
        click.echo('Fetched {} @{}, id={}'.format(
            self.created_at.strftime('%Y-%m-%d'),
            self.user_screen_name,
            self.status_id))


def create_db(database_path):
    engine = create_engine('sqlite:///{}'.format(database_path))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return session()
