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
    tweet_id = Column(Integer)
    lang = Column(String)
    source = Column(String)
    text = Column(String)
    is_retweet = Column(Boolean)
    is_deleted = Column(Boolean)
    exclude_from_delete = Column(Boolean)

    def __init__(self, api_data):
        self.create_at = datetime.strptime(api_data.created_at, '%a %b %d %H:%M:%S +0000 %Y')
        self.tweet_id = api_data.id
        self.lang = api_data.lang
        self.source = api_data.source
        self.text = api_data.text
        self.is_retweet = api_data.retweeted
        self.is_deleted = False
        self.exclude_from_delete = False


def create_db(database_path):
    engine = create_engine('sqlite:///{}'.format(database_path))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return session()
