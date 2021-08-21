from marshmallow_dataclass import dataclass


@dataclass
class GeneralUserEntry:
    uid: int
    username: str
    email: str
