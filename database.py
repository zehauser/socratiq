import os

from sqlalchemy import Column, String, DateTime, LargeBinary, ForeignKey, Table
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
    secret_value = Column(String(128), nullable=False)

user_followers = Table('UserFollowers', Base.metadata,
    Column('follower', String(25), ForeignKey('Users.id'), primary_key=True),
    Column('followee', String(25), ForeignKey('Users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'Users'
    id = Column(String(25), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    time_created = Column(DateTime, nullable=False)
    password_data = relationship('PasswordData')
    users_followed = relationship('User', lazy='dynamic', secondary=user_followers,
                                  primaryjoin=(user_followers.c.follower == id),
                                  secondaryjoin=(user_followers.c.followee == id))

class PasswordData(Base):
    __tablename__ = 'PasswordData'
    userid = Column(String(25), ForeignKey('Users.id'), primary_key=True)
    salt = Column(LargeBinary(32), nullable=False)
    hash = Column(LargeBinary(32), nullable=False)

Base.metadata.create_all(engine, checkfirst=True) 

JWT_SECRET = Session().query(Secret).get('JWT_SECRET').secret_value
