import json
import webapp2
import logging

import sqlalchemy.exc

from common import authentication
from common.database import Session, User

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

_ERR_PREFIX = '(1406, "Data too long for column \''


class Endpoint(webapp2.RequestHandler):
    def dispatch(self):
        self.authenticated_user = None
        if 'Authorization' in self.request.headers:
            auth_header = self.request.headers['Authorization']
            auth_token = auth_header[7:]  # len("Bearer ") is 7
            user = authentication.decode_token(auth_token)
            if not auth_header.startswith('Bearer ') or not user:
                self.error(401)
                return
            else:
                self.authenticated_user = user

        self.response.headers['Access-Control-Allow-Origin'] = (
            self.request.headers.get('Origin', '*'))
        self.response.headers['Access-Control-Allow-Credentials'] = 'true'
        self.response.headers['Access-Control-Allow-Methods'] = (
            'GET, POST, PUT, DELETE, OPTIONS, PATCH')
        self.response.headers['Access-Control-Allow-Headers'] = (
            'Authorization, Content-Length, Content-Type')
        self.response.headers['Access-Control-Expose-Headers'] = (
            self.response.headers['Access-Control-Allow-Headers'])

        self.db_session = Session()
        super(Endpoint, self).dispatch()
        self.db_session.close()

    def json_response(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(obj) + "\r\n")

    def get_user(self, userid):
        return self.db_session.query(User).get(userid)

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
        if (isinstance(exn, sqlalchemy.exc.DataError)
            and _ERR_PREFIX in exn.message):
            print exn.message
            column_start_i = exn.message.find(_ERR_PREFIX) + len(_ERR_PREFIX)
            column_end_i = exn.message.find('\'', column_start_i)
            column = exn.message[column_start_i:column_end_i]
            self.error(422, json={
                'code': 'ATTRIBUTE_LENGTH_EXCEEDED',
                'attribute': column
            })
        else:
            logging.exception(exn)
            self.error(500)

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


def requires_authentication(as_param=None, as_key=None):
    def requires_authentication_decorator_creator(handler_func):
        def requires_authentication_decorator(self, *args, **kwargs):
            if not self.authenticated_user:
                self.error(401)
            elif as_param and kwargs[as_param] != self.authenticated_user:
                self.error(403)
            elif as_key and (self.json_request[as_key]
                                 != self.authenticated_user):
                self.error(403)
            else:
                handler_func(self, *args, **kwargs)

        return requires_authentication_decorator

    return requires_authentication_decorator_creator


class SchemaError(StandardError):
    def __init__(self, code, **kwargs):
        kwargs['code'] = code
        self.message = kwargs


def assert_json_matches_schema(schema, obj):
    if isinstance(schema, dict):
        if not isinstance(obj, dict):
            raise SchemaError('EXPECTED_JSON_OBJECT', received=obj)
        for k in set(schema.keys()):
            if k not in obj.keys():
                raise SchemaError('MISSING_BODY_KEY', expected=k)
        for k in set(obj.keys()):
            if k not in schema.keys():
                raise SchemaError('UNEXPECTED_BODY_KEY', received=k)
        for key, type in schema.iteritems():
            assert_json_matches_schema(type, obj[key])
    elif isinstance(schema, list):
        if not isinstance(obj, list):
            raise SchemaError('EXPECTED_JSON_ARRAY', received=obj)
        type = schema[0]
        for val in obj:
            assert_json_matches_schema(type, val)
    else:
        type = schema
        if schema == str:
            type = unicode
        if not isinstance(obj, type):
            raise SchemaError('TYPE_MISMATCH', received=obj,
                              expected=schema.__name__)


def request_schema(schema):
    def request_schema_decorator_creator(handler_func):
        def request_schema_decorator(self, *args, **kwargs):
            try:
                if schema is None:
                    if self.request.body != "":
                        raise SchemaError('BODY_NOT_EMPTY')
                else:
                    self.json_request = json.loads(self.request.body)
                    assert_json_matches_schema(schema, self.json_request)
            except SchemaError, e:
                self.error(400, json=e.message)
            except ValueError:
                self.error(400, json={'code': 'BODY_JSON_INVALID'})
            else:
                handler_func(self, *args, **kwargs)

        return request_schema_decorator

    return request_schema_decorator_creator
