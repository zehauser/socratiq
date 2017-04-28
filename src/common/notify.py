from twilio.rest import Client
import logging

from common.database import Session, Secret

try:
    _session = Session()
    _TWILIO_ACCOUNT = _session.query(Secret).get('TWILIO_ACCOUNT').secret_value
    _TWILIO_TOKEN = _session.query(Secret).get('TWILIO_TOKEN').secret_value
    _ADMIN_PHONE = _session.query(Secret).get('ADMIN_PHONE').secret_value
    _TWILIO_PHONE = _session.query(Secret).get('TWILIO_PHONE').secret_value
    _session.close()
    _client = Client(_TWILIO_ACCOUNT, _TWILIO_TOKEN)
except StandardError, e:
    logging.error('Error setting up Twilio!', exc_info=e)

def notify_administrator(url, exn):
    try:
        _client.messages.create(
            to=_ADMIN_PHONE,
            from_=_TWILIO_PHONE,
            body='[{}] {}'.format(url, exn.__repr__())
        )
    except StandardError, e:
        logging.error('Error sending Twilio message!', exc_info=e)