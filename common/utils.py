import flask
from functools import wraps
# from utils import


def unpack_argument(func):
    @wraps(func)
    def wrapper():
        data = flask.request.get_json() or {}
        return func(**data)
    return wrapper