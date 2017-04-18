import os

from sqlalchemy import Column, String, DateTime, LargeBinary, ForeignKey, Table, \
    Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

_CONNECTION_STR = 'mysql+mysqldb://{}@/{}?unix_socket=/cloudsql/{}'.format(
    os.environ.get('CLOUDSQL_USER'), os.environ.get('CLOUDSQL_DB'),
    os.environ.get('CLOUDSQL_CONNECTION_NAME')
)

_ECHO = False
if not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    _ECHO = True
    _CONNECTION_STR = "mysql+mysqldb://root@127.0.0.1:9501/v3"

_engine = create_engine(_CONNECTION_STR, echo=_ECHO)
Session = sessionmaker(bind=_engine)
_Base = declarative_base()
_Base.metadata.bind = _engine


class Secret(_Base):
    __tablename__ = 'Secrets'
    secret_id = Column(String(25), primary_key=True)
    secret_value = Column(LargeBinary(128), nullable=False)


user_follows = Table(
    'UserFollows', _Base.metadata,
    Column('follower', String(25), ForeignKey('Users.id'), primary_key=True),
    Column('followee', String(25), ForeignKey('Users.id'), primary_key=True)
)

tag_follows = Table(
    'TagFollows', _Base.metadata,
    Column('follower', String(25), ForeignKey('Users.id'), primary_key=True),
    Column('tag', String(25), ForeignKey('Tags.name'), primary_key=True)
)


class User(_Base):
    __tablename__ = 'Users'
    id = Column(String(25), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    time_created = Column(DateTime, nullable=False)

    password_data = relationship('PasswordData')
    followers = relationship('User', lazy='dynamic',
                             secondary=user_follows,
                             primaryjoin=user_follows.c.followee == id,
                             secondaryjoin=user_follows.c.follower == id)
    users_followed = relationship('User', lazy='dynamic',
                                  secondary=user_follows,
                                  primaryjoin=user_follows.c.follower == id,
                                  secondaryjoin=user_follows.c.followee == id)
    tags_followed = relationship('Tag', lazy='dynamic', secondary=tag_follows)
    articles_authored = relationship('Article', back_populates='author')


class PasswordData(_Base):
    __tablename__ = 'PasswordData'
    userid = Column(String(25), ForeignKey('Users.id'), primary_key=True)
    salt = Column(LargeBinary(32), nullable=False)
    hash = Column(LargeBinary(32), nullable=False)


_article_tags = Table(
    'ArticleTags', _Base.metadata,
    Column('article', String(32), ForeignKey('Articles.uuid'),
           primary_key=True),
    Column('tag', String(25), ForeignKey('Tags.name'), primary_key=True)
)


class Tag(_Base):
    __tablename__ = 'Tags'
    name = Column(String(25), primary_key=True)


class Article(_Base):
    __tablename__ = 'Articles'
    uuid = Column(String(32), primary_key=True)
    author_id = Column(String(25), ForeignKey('Users.id'), nullable=False)
    title = Column(String(50), nullable=False)
    time_published = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    author = relationship('User', back_populates='articles_authored')
    tags = relationship('Tag', secondary=_article_tags,
                        primaryjoin=_article_tags.c.article == uuid)


# Not sure why this can't go in the initial Tag class definition, but
# SQLAlchemy throws a fit (but only when running on actual GAE, not when
# using the local dev server).
Tag.articles = relationship('Article', secondary=_article_tags,
                            primaryjoin=_article_tags.c.tag == Tag.name)


class Comment(_Base):
    __tablename__ = 'Comments'
    uuid = Column(String(32), primary_key=True)
    author_id = Column(String(25), ForeignKey('Users.id'), nullable=False)
    article_id = Column(String(32), ForeignKey('Articles.uuid'), nullable=False)
    time_published = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    author = relationship('User')
    article = relationship('Article')


_Base.metadata.create_all(_engine, checkfirst=True)
