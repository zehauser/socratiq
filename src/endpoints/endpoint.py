import json
import logging

import sqlalchemy.exc
import webapp2

from common import authentication, running_in_production
from common.authentication import InvalidAuthenticationError
from common.database import Session
from common.notify import notify_administrator

DEFAULT_ERRORS = {
    400: "400 Bad Request. The request body does not conform to the schema " +
         "required by this resource.\r\n",

    401: "401 Unauthorized. This resource requires authentication via a " +
         "valid, unexpired token issued by the /login resource.\r\n",

    403: "403 Forbidden. User is not authorized to perform the requested " +
         "operation on this resource.\r\n",

    404: "404 Not Found. The requested resource does not exist.\r\n",

    405: "405 Method Not Allowed. The requested HTTP method cannot be " +
         "applied to the requested resource.\r\n",

    409: "409 Conflict. The specified resource already exists.\r\n",

    422: "422 Unprocessable Entity. Some element(s) of the request you " +
         "submitted violate preconditions of this resource.\r\n",

    500: "500 Internal Server Error. Sorry - no further information is " +
         "available.\r\n",

    501: "501 Not Implemented. The requested HTTP method has not yet been " +
         "implemented on this server.\r\n"
}


class Endpoint(webapp2.RequestHandler):
    def dispatch(self):
        try:
            logging.debug(self.request)
            self.authenticated_user = None
            self.db_session = Session()
            self.request_data = {}

            self._process_auth_header()
            self._add_cors_headers()
            super(Endpoint, self).dispatch()
            self.db_session.close()

        except InvalidAuthenticationError:
            self.error(401)

    def _process_auth_header(self):
        if 'Authorization' in self.request.headers:
            auth_header = self.request.headers['Authorization']
            if not auth_header.startswith('Bearer '):
                raise InvalidAuthenticationError
            auth_token = auth_header[7:]  # len("Bearer ") is 7
            self.authenticated_user = authentication.decode_token(auth_token)

    def _add_cors_headers(self):
        self.response.headers['Access-Control-Allow-Origin'] = (
            self.request.headers.get('Origin', '*'))
        self.response.headers['Access-Control-Allow-Credentials'] = 'true'
        self.response.headers['Access-Control-Allow-Methods'] = (
            'GET, POST, PUT, DELETE, OPTIONS, PATCH')
        self.response.headers['Access-Control-Allow-Headers'] = (
            'Authorization, Content-Length, Content-Type')
        self.response.headers['Access-Control-Expose-Headers'] = (
            self.response.headers['Access-Control-Allow-Headers'])

    def json_response(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(obj) + "\r\n")

    def error(self, code, msg=None, json=None):
        self.response.clear()
        self.response.set_status(code)
        self.response.headers['Content-Type'] = 'text/plain'
        if code == 401:
            self.response.headers['WWW-Authenticate'] = 'Bearer'
        if msg == None:
            msg = DEFAULT_ERRORS[code]
        if json:
            self.json_response(json)
        else:
            self.response.write(msg)

    def handle_exception(self, exn, debug_mode):
        ERR_PREFIX = '(1406, "Data too long for column \''
        if (isinstance(exn, sqlalchemy.exc.DataError)
            and ERR_PREFIX in exn.message):
            column_start_i = exn.message.find(ERR_PREFIX) + len(ERR_PREFIX)
            column_end_i = exn.message.find('\'', column_start_i)
            column = exn.message[column_start_i:column_end_i]
            self.error(422, json={
                'code': 'ATTRIBUTE_LENGTH_EXCEEDED',
                'attribute': column
            })
        else:
            logging.exception(exn)
            self.error(500)
            if running_in_production():
                notify_administrator(
                    self.request.method + ' ' + self.request.url, exn)

    def get(self, *args, **kwargs):
        self.error(405)

    def head(self, *args, **kwargs):
        self.error(501, "")

    def post(self, *args, **kwargs):
        self.error(405)

    def put(self, *args, **kwargs):
        self.error(405)

    def delete(self, *args, **kwargs):
        self.error(405)

    def connect(self, *args, **kwargs):
        self.error(405)

    def options(self, *args, **kwargs):
        self.response.set_status(200)

    def trace(self, *args, **kwargs):
        self.error(405)

    def patch(self, *args, **kwargs):
        self.error(405)


class NotFoundHandler(Endpoint):
    def dispatch(self):
        self.error(404)
