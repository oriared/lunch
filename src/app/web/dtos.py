from dataclasses import dataclass


@dataclass
class RequestUserDTO:
    id: int
    username: str
    name: str
    is_admin: bool
