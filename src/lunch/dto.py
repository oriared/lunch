from dataclasses import dataclass


@dataclass
class Lunch:
    dish_mode: str
    first_dish: str
    second_dish_first_part: str
    second_dish_second_part: str = ''
