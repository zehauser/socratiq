import os
from datetime import datetime, timedelta

import jwt
from jwt.exceptions import *
from database import PasswordData, Secret, Session
from Crypto.Protocol import KDF

jwt_secret = Session().query(Secret).get('JWT_SECRET')
if jwt_secret:
    JWT_SECRET = jwt_secret.secret_value
else:
    JWT_SECRET = os.urandom(128)
    session = Session()
    session.add(Secret(secret_id='JWT_SECRET', secret_value=JWT_SECRET))
    session.commit()

def issue_token(userid, password_data, password):
    if password_data:
        if password_data.hash == password_hash(password, password_data.salt):
            token_expiry = datetime.utcnow() + timedelta(hours=1)
            token_payload = { 'userid': userid, 'exp': token_expiry }
            return jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
    return None

def decode_token(token):
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=['HS256'], 
            options={'require_exp': True}
        )
        if 'userid' not in payload: 
            raise MissingRequiredClaimError
        return payload['userid']
    except (DecodeError, ExpiredSignatureError, MissingRequiredClaimError):
        return None

def password_hash(password, salt):
    return KDF.PBKDF2(password, salt, dkLen=32, count=10000)

def create_password(userid, password):
    salt = os.urandom(32)
    hash = password_hash(password, salt)
    return PasswordData(userid=userid, salt=salt, hash=hash)

