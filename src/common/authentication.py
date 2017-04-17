import os
import jwt
import Crypto.Protocol
from datetime import datetime, timedelta

from common.database import PasswordData, Secret, Session

_jwt_secret = Session().query(Secret).get('JWT_SECRET')
if _jwt_secret:
    _JWT_SECRET = _jwt_secret.secret_value
else:
    _JWT_SECRET = os.urandom(128)
    _session = Session()
    _session.add(Secret(secret_id='JWT_SECRET', secret_value=_JWT_SECRET))
    _session.commit()


def _password_hash(password, salt):
    return Crypto.Protocol.KDF.PBKDF2(password, salt, dkLen=32, count=10000)


def issue_token(userid, password_data, password):
    if password_data:
        if password_data.hash == _password_hash(password, password_data.salt):
            token_expiry = datetime.utcnow() + timedelta(hours=1)
            token_payload = {'userid': userid, 'exp': token_expiry}
            return jwt.encode(token_payload, _JWT_SECRET, algorithm='HS256')
    return None


def decode_token(token):
    try:
        payload = jwt.decode(
            token, _JWT_SECRET, algorithms=['HS256'],
            options={'require_exp': True}
        )
        if 'userid' not in payload:
            raise jwt.MissingRequiredClaimError
        return payload['userid']
    except (jwt.DecodeError, jwt.ExpiredSignatureError,
            jwt.MissingRequiredClaimError):
        return None


def create_password_data(userid, password):
    salt = os.urandom(32)
    hash = _password_hash(password, salt)
    return PasswordData(userid=userid, salt=salt, hash=hash)
