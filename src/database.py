import os
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, LargeBinary, ForeignKey, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_DB = 'v2'
CONNECTION_STR = 'mysql+mysqldb://{}@/{}?unix_socket=/cloudsql/{}'.format(
    CLOUDSQL_USER, CLOUDSQL_DB, CLOUDSQL_CONNECTION_NAME
)

if not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'): 
    CONNECTION_STR = "mysql+mysqldb://root@127.0.0.1:9501/v2"

engine = create_engine(CONNECTION_STR)
Session = sessionmaker(bind=engine)
Base = declarative_base()
Base.metadata.bind = engine

class Secret(Base):
    __tablename__ = 'Secrets'
    secret_id = Column(String(25), primary_key=True)
    secret_value = Column(LargeBinary(128), nullable=False)

user_follows = Table('UserFollows', Base.metadata,
    Column('follower', String(25), ForeignKey('Users.id'), primary_key=True),
    Column('followee', String(25), ForeignKey('Users.id'), primary_key=True)
)

tag_follows = Table('TagFollows', Base.metadata,
    Column('follower', String(25), ForeignKey('Users.id'), primary_key=True),
    Column('tag', String(25), ForeignKey('Tags.name'), primary_key=True)
)

class User(Base):
    __tablename__ = 'Users'
    id = Column(String(25), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    time_created = Column(DateTime, nullable=False)

    password_data = relationship('PasswordData')
    users_followed = relationship('User', lazy='dynamic', 
                                  secondary=user_follows,
                                  primaryjoin=user_follows.c.follower == id,
                                  secondaryjoin=user_follows.c.followee == id)
    tags_followed = relationship('Tag', lazy='dynamic', secondary=tag_follows)
    articles_authored = relationship('Article', back_populates='author')

class PasswordData(Base):
    __tablename__ = 'PasswordData'
    userid = Column(String(25), ForeignKey('Users.id'), primary_key=True)
    salt = Column(LargeBinary(32), nullable=False)
    hash = Column(LargeBinary(32), nullable=False)

article_tags = Table('ArticleTags', Base.metadata,
    Column('article', String(32), ForeignKey('Articles.uuid'), primary_key=True),
    Column('followee', String(25), ForeignKey('Users.id'), primary_key=True)
)

class Tag(Base):
    __tablename__ = 'Tags'
    name = Column(String(25), primary_key=True)

    articles = relationship('Article', secondary=article_tags)

class Article(Base):
    __tablename__ = 'Articles'
    uuid = Column(String(32), primary_key=True)
    author_id = Column(String(25), ForeignKey('Users.id'), nullable=False)
    title = Column(String(50), nullable=False)
    time_published = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    
    author = relationship('User', back_populates='articles_authored')
    tags = relationship('Tag', secondary=article_tags)

class Comment(Base):
    __tablename__ = 'Comments'
    uuid = Column(String(32), primary_key=True)
    author_id = Column(String(25), ForeignKey('Users.id'), nullable=False)
    article_id = Column(String(32), ForeignKey('Articles.uuid'), nullable=False)
    time_published = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    
    author = relationship('User')
    article = relationship('Article')

Base.metadata.create_all(engine, checkfirst=True) 