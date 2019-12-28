from dataclasses import dataclass
from json import JSONDecoder, JSONEncoder


def load_from_json(cls, json):
    return cls(**JSONDecoder().decode(json))


class TokenBase:
    def as_json(self) -> str:
        return JSONEncoder().encode(self.__dict__)


@dataclass
class PasswordResetToken(TokenBase):
    uid: int
    expire_after: int
    token: str


@dataclass
class RegisterToken(TokenBase):
    username: str
    expire_after: int
    password: str
    email: str
    token: str
