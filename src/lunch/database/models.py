import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    password: str
    joined_dt: datetime.datetime
    is_admin: bool = False
    is_active: bool = True
    name: str = ''


@dataclass
class Order:
    id: int
    date: datetime.date
    dishes_text: str
    user_id: int | None = None
    comment: str | None = None


@dataclass
class Dish:
    id: int
    name: str


@dataclass
class Category:
    id: int
    name: str
    parent_id: int | None


@dataclass
class DishCategory:
    dish_id: int
    category_id: int


@dataclass
class OrderDish:
    order_id: int
    dish_id: int
    count: int
