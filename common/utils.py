from typing import Any
import flask
from functools import wraps
import jsonpickle
from marshmallow import ValidationError


def get_uid() -> int:
    return flask.session.get("uid", -1)


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
                return make_json_response(-1, message=f"Missing Header: {name}")
            return func(*args, **kwargs)
        return _wrapper
    return wrapper


def require_schema(schema: Any):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            data = flask.request.get_json() or {}
            try:
                data = schema.load(data)
            except ValidationError as ex:
                return make_json_response(-1, message=str(ex.messages))
            args = schema.fields
            return func(**{k: getattr(data, k) for k in args.keys()})
        return _wrapper
    return wrapper


