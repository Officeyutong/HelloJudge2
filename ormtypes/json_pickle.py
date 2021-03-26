import sqlalchemy.types as types
from sqlalchemy.dialects import mysql
# from jsonpickle import encode, decode
from ujson import encode, decode

class JsonPickle(types.TypeDecorator):
    impl = mysql.LONGTEXT

    def process_bind_param(self, value, dialect):
        # print("encoding {}".format(value))
        return encode(value)

    def process_result_value(self, value, dialect):
        # print("decoding {}".format(value))
        return decode(value)

