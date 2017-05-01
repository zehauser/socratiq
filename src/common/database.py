import os
import logging
from sqlalchemy import Column, String, DateTime, LargeBinary, ForeignKey, Table, \
    Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

from common import running_in_production

_CONNECTION_STR = 'mysql+mysqldb://{}@/{}?unix_socket=/cloudsql/{}&charset=utf8'.format(
    os.environ.get('CLOUDSQL_USER'), os.environ.get('CLOUDSQL_DB'),
    os.environ.get('CLOUDSQL_CONNECTION_NAME')
)

if not running_in_production():
    _CONNECTION_STR = "mysql+mysqldb://root@127.0.0.1:9501/v3?charset=utf8"

_engine = create_engine(_CONNECTION_STR)
Session = sessionmaker(bind=_engine)
_Base = declarative_base()
_Base.metadata.bind = _engine


class Secret(_Base):
    __tablename__ = 'Secrets'
    secret_id = Column(String(25), primary_key=True)
    secret_value = Column(LargeBinary(128), nullable=False)


_user_follows = Table(
    'UserFollows', _Base.metadata,
    Column('follower', String(50), ForeignKey('Users.id'), primary_key=True),
    Column('followee', String(50), ForeignKey('Users.id'), primary_key=True)
)

_tag_follows = Table(
    'TagFollows', _Base.metadata,
    Column('follower', String(50), ForeignKey('Users.id'), primary_key=True),
    Column('tag', String(100), ForeignKey('Tags.name'), primary_key=True)
)


class User(_Base):
    __tablename__ = 'Users'
    id = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    institution = Column(String(125), ForeignKey('Institutions.name'),
                         nullable=False)
    time_created = Column(DateTime, nullable=False)

    password_data = relationship('PasswordData')
    followers = relationship('User', lazy='dynamic',
                             secondary=_user_follows,
                             primaryjoin=_user_follows.c.followee == id,
                             secondaryjoin=_user_follows.c.follower == id)
    users_followed = relationship('User', lazy='dynamic',
                                  secondary=_user_follows,
                                  primaryjoin=_user_follows.c.follower == id,
                                  secondaryjoin=_user_follows.c.followee == id)
    tags_followed = relationship('Tag', lazy='dynamic', secondary=_tag_follows)
    articles_authored = relationship('Article', lazy='dynamic',
                                     back_populates='author')


class PasswordData(_Base):
    __tablename__ = 'PasswordData'
    userid = Column(String(50), ForeignKey('Users.id'), primary_key=True)
    salt = Column(LargeBinary(32), nullable=False)
    hash = Column(LargeBinary(32), nullable=False)


_article_tags = Table(
    'ArticleTags', _Base.metadata,
    Column('article', String(32), ForeignKey('Articles.uuid'),
           primary_key=True),
    Column('tag', String(100), ForeignKey('Tags.name'), primary_key=True)
)


class Tag(_Base):
    __tablename__ = 'Tags'
    name = Column(String(100), primary_key=True)

    followers = relationship('User', lazy='dynamic', secondary=_tag_follows)


class Article(_Base):
    __tablename__ = 'Articles'
    uuid = Column(String(32), primary_key=True)
    author_id = Column(String(50), ForeignKey('Users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    time_published = Column(DateTime, nullable=False, index=True)
    content = Column(Text, nullable=False)

    author = relationship('User', back_populates='articles_authored')
    tags = relationship('Tag', lazy='dynamic', secondary=_article_tags,
                        primaryjoin=_article_tags.c.article == uuid)
    # comments = relationship('Comment', lazy='dynamic')


# Not sure why this can't go in the initial Tag class definition, but
# SQLAlchemy throws a fit (but only when running on actual GAE, not when
# using the local dev server).
Tag.articles = relationship('Article', lazy='dynamic', secondary=_article_tags,
                            primaryjoin=_article_tags.c.tag == Tag.name)


class Comment(_Base):
    __tablename__ = 'Comments'
    uuid = Column(String(32), primary_key=True)
    author_id = Column(String(50), ForeignKey('Users.id'), nullable=False)
    article_id = Column(String(32), ForeignKey('Articles.uuid'), nullable=False)
    time_published = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    author = relationship('User')
    article = relationship('Article', backref='comments')


class Institution(_Base):
    __tablename__ = 'Institutions'
    name = Column(String(125), primary_key=True)
    domain = Column(String(50), nullable=False)


_Base.metadata.create_all(_engine, checkfirst=True)


def userid_does_follow(follower_id, tag=None, user=None):
    # assert (tag and isinstance(tag, Tag)) or (user and isinstance(user, User))
    assert isinstance(follower_id, basestring)
    if user:
        return user.followers.filter_by(id=follower_id).count() == 1
    if tag:
        return tag.followers.filter_by(id=follower_id).count() == 1

# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
