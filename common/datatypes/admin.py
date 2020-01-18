from dataclasses import dataclass
from typing import List
@dataclass
class UserPermission:
    uid: int
    username: str
    permissions: List[str]
