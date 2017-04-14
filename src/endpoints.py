import webapp2

import json
from database import Session, User
from authentication import decode_token

DEFAULT_ERRORS = {
    400: "400 Bad Request! The request body does not conform to the schema " +
         "required by this resource.\r\n",
    401: "401 Unauthorized! This resource requires authentication via a " +
         "valid, unexpired token issued by the /login resource.\r\n",
    403: "403 Forbidden! User is not authorized to perform the requested " + 
         "operation on this resource.\r\n",
    404: "404 Not Found! The requested resource does not exist.\r\n",
    409: "409 Conflict! The specified resource already exists.\r\n"
}

class Endpoint(webapp2.RequestHandler):
    def dispatch(self):
        self.db_session = Session()
        self.authenticated_user = None
        if 'Authorization' in self.request.headers:
            auth_header = self.request.headers['Authorization']
            auth_token = auth_header[7:] # len("Bearer ") is 7
            user = decode_token(auth_token)
            if not auth_header.startswith('Bearer ') or not user:
                self.error(401)
                return
            else:
                self.authenticated_user = user
        super(Endpoint, self).dispatch()

    def json_response(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(obj) + "\r\n")

    def get_user(self, userid):
        return self.db_session.query(User).get(userid)

    def error(self, code, msg=None):
        self.response.set_status(code)
        self.response.headers['Content-Type'] = 'text/plain'
        if code == 401:
            self.response.headers['WWW-Authenticate'] = 'Bearer'
        if msg == None:
            msg = DEFAULT_ERRORS[code]
        self.response.write(msg)

def requires_authentication(as_param):
    def requires_authentication_decorator_creator(handler_func):
        def requires_authentication_decorator(self, *args, **kwargs):
            if not self.authenticated_user:
                self.error(401)
            elif kwargs[as_param] != self.authenticated_user:
                self.error(403)
            else:
                handler_func(self, *args, **kwargs)
        return requires_authentication_decorator
    return requires_authentication_decorator_creator

class ValidationError(Exception):
    pass

def require(assertion):
    if not assertion:
        raise ValidationError

def request_schema(schema):
    def request_schema_decorator_creator(handler_func):
        def request_schema_decorator(self, *args, **kwargs):
            try:
                if schema is None:
                    require(self.request.body == "")
                else:
                    self.json_request = json.loads(self.request.body)
                    require(set(self.json_request.keys()) == set(schema.keys()))
                    for k,typ in schema.iteritems():
                        if typ == str:
                            require(isinstance(self.json_request[k], unicode)) 
            except (ValidationError, ValueError):
                self.error(400)
            else:
                handler_func(self, *args, **kwargs)

        return request_schema_decorator
    return request_schema_decorator_creator