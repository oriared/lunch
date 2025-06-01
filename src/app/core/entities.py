import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    username: str
    password: str
    joined_dt: datetime.datetime
    is_admin: bool = False
    is_active: bool = True
    name: str = ''


@dataclass
class Order:
    id: int | None
    date: datetime.date
    user_id: int | None = None
    comment: str | None = None


@dataclass
class Category:
    id: int | None
    code: str
    name: str


@dataclass
class Dish:
    id: int | None
    name: str
    weekday: int | None = None
