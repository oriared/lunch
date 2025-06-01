import datetime
from dataclasses import dataclass


@dataclass
class UserCreateOrUpdateDTO:
    id: int | None = None
    username: str | None = None
    password: str | None = None
    name: str | None = None
    is_admin: bool | None = None
    is_active: bool | None = None
    joined_dt: datetime.datetime | None = None
