import os
import jwt
from Crypto.Protocol import KDF
from datetime import datetime, timedelta

from common.database import PasswordData, Secret, Session

_TOKEN_HOURS = 12
_HASH_ITERATIONS = 10000

_session = Session()
_jwt_secret = _session.query(Secret).get('JWT_SECRET')
if _jwt_secret:
    _JWT_SECRET = _jwt_secret.secret_value
else:
    _JWT_SECRET = os.urandom(128)
    _session.add(Secret(secret_id='JWT_SECRET', secret_value=_JWT_SECRET))
    _session.commit()
_session.close()

class InvalidAuthenticationError(StandardError):
    pass

def _password_hash(password, salt):
    return KDF.PBKDF2(password, salt, dkLen=32, count=_HASH_ITERATIONS)


def issue_token(userid, password_data, password):
    if password_data:
        if password_data.hash == _password_hash(password, password_data.salt):
            token_expiry = datetime.utcnow() + timedelta(hours=_TOKEN_HOURS)
            token_payload = {'userid': userid, 'exp': token_expiry}
            return jwt.encode(token_payload, _JWT_SECRET, algorithm='HS256')
    raise InvalidAuthenticationError


def decode_token(token):
    try:
        payload = jwt.decode(
            token, _JWT_SECRET,
            algorithms=['HS256'],
            options={'require_exp': True}
        )
        return payload['userid']
    except (jwt.DecodeError, jwt.ExpiredSignatureError,
            jwt.MissingRequiredClaimError):
        raise InvalidAuthenticationError


def create_password_data(userid, password):
    salt = os.urandom(32)
    hash = _password_hash(password, salt)
    return PasswordData(userid=userid, salt=salt, hash=hash)
