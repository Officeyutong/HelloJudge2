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

def require_header(name: str, value: str):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            if flask.request.headers.get(name, None) != value:
                return make_json_response(-1, message=f"缺少 Header: {name}")
            return func(*args, **kwargs)
        return _wrapper
    return wrapper
