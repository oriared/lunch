from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str = ''
    email: str = ''
    is_admin: bool = False


@dataclass
class Lunch:
    dish_mode: str
    first_dish: str
    second_dish_first_part: str
    second_dish_second_part: str = ''
