import flask
from functools import wraps
import jsonpickle


def unpack_argument(func):
    @wraps(func)
    def wrapper():
        data = flask.request.get_json() or {}
        return func(**data)
    return wrapper


def make_json_response(code, **kwargs):
    return jsonpickle.dumps({
        "code": code,
        **kwargs
    }, unpicklable=False)
