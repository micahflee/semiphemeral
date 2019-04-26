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
    in_reply_to_screen_name = Column(String)
    in_reply_to_user_id = Column(Integer)
    lang = Column(String)
    source = Column(String)
    text = Column(String)
    is_retweet = Column(Boolean)
    is_deleted = Column(Boolean)
    exclude_from_delete = Column(Boolean)


def create_db(database_path):
    engine = create_engine('sqlite:///{}'.format(database_path))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return session
