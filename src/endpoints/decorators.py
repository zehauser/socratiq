import json

def requires_authentication(as_param=None, as_key=None):
    def requires_authentication_decorator_creator(handler_func):
        def requires_authentication_decorator(self, *args, **kwargs):
            if not self.authenticated_user:
                self.error(401)
            elif as_param and kwargs[as_param] != self.authenticated_user:
                self.error(403)
            elif as_key and (self.request_data[as_key]
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


def request_schema(required_body=None, optional_params=None):
    def request_schema_decorator_creator(handler_func):
        def request_schema_decorator(self, *args, **kwargs):
            try:
                if required_body is None:
                    if self.request.body != "":
                        raise SchemaError('BODY_NOT_EMPTY')
                else:
                    self.request_data = json.loads(self.request.body)
                    assert_json_matches_schema(required_body, self.request_data)

                for k, v in self.request.GET.items():
                    if k not in optional_params:
                        raise SchemaError('UNEXPECTED_QUERY_PARAM', received=k)
                    if k in self.request_data:
                        raise SchemaError('DUPLICATE_QUERY_PARAM', received=k)
                    self.request_data[k] = v

            except SchemaError, e:
                self.error(400, json=e.message)
            except ValueError:
                self.error(400, json={'code': 'BODY_JSON_INVALID'})
            else:
                handler_func(self, *args, **kwargs)

        return request_schema_decorator

    return request_schema_decorator_creator