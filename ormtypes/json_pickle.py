import sqlalchemy.types as types
from jsonpickle import encode, decode


class JsonPickle(types.TypeDecorator):
    impl = types.Text

    def process_bind_param(self, value, dialect):
        return encode(value)

    def process_result_value(self, value, dialect):
        return decode(value)

    def copy(self, **kw):
        return JsonPickle(self.impl.length)
