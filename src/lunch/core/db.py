import datetime
from dataclasses import dataclass

from core import consts, entities


@dataclass
class DishCategory:
    dish_id: int
    category_code: str


@dataclass
class OrderDish:
    order_id: int
    dish_id: int


users: list[entities.User] = [
    entities.User(1, 'admin', 'admin', datetime.datetime(2024, 10, 20, 10, 47), is_admin=True),
    entities.User(2, 'iar', 'admin', datetime.datetime(2024, 10, 20, 10, 30), is_admin=False, name='Ярослав Орлов'),
    entities.User(3, 'abandoned', 'admin', datetime.datetime(2024, 10, 16, 14, 15), is_admin=False),
    entities.User(4, 'dzhamil', 'admin', datetime.datetime(2024, 10, 14, 20, 22), is_admin=False, name='Джамиль'),
]

orders: list[entities.Order] = []

dishes: list[entities.Dish] = [
    entities.Dish(1, 'Бургер'),
    entities.Dish(2, 'Салат'),
    entities.Dish(3, 'Пицца'),
    entities.Dish(4, 'Компот'),
    entities.Dish(5, 'Кола'),
    entities.Dish(6, 'Кофе', 2),
    entities.Dish(7, 'Картофель', 3),
    entities.Dish(8, 'Мясо'),
    entities.Dish(9, 'Сыр'),
    entities.Dish(10, 'Салат овощной'),
    entities.Dish(11, 'Паста'),
    entities.Dish(12, 'Суп', 4),
    entities.Dish(13, 'Борщ'),
    entities.Dish(14, 'Рис'),
    entities.Dish(15, 'Хлеб'),
    entities.Dish(16, 'Пельмени'),
    entities.Dish(17, 'Филе куриное', 1),
    entities.Dish(18, 'Куриное филе', 6),
    entities.Dish(19, 'Рыба', 6),
    entities.Dish(20, 'Котлета'),
    entities.Dish(21, 'Грибы'),
    entities.Dish(22, 'Шашлык'),
]

dishes_categories: list[DishCategory] = [
    DishCategory(1, consts.CategoryCode.FIRST),
    DishCategory(2, consts.CategoryCode.FIRST),
    DishCategory(3, consts.CategoryCode.FIRST),
    DishCategory(4, consts.CategoryCode.FIRST),
    DishCategory(5, consts.CategoryCode.FIRST),
    DishCategory(6, consts.CategoryCode.FIRST),
    DishCategory(7, consts.CategoryCode.FIRST),
    DishCategory(8, consts.CategoryCode.FIRST),
    DishCategory(6, consts.CategoryCode.VEGAN),
    DishCategory(7, consts.CategoryCode.VEGAN),
    DishCategory(8, consts.CategoryCode.VEGAN),
    DishCategory(9, consts.CategoryCode.SECOND_STANDARD),
    DishCategory(10, consts.CategoryCode.SECOND_STANDARD),
    DishCategory(11, consts.CategoryCode.SECOND_STANDARD),
    DishCategory(12, consts.CategoryCode.SECOND_STANDARD),
    DishCategory(13, consts.CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART),
    DishCategory(14, consts.CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART),
    DishCategory(15, consts.CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART),
    DishCategory(16, consts.CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART),
    DishCategory(17, consts.CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART),
    DishCategory(18, consts.CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART),
    DishCategory(19, consts.CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART),
    DishCategory(20, consts.CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART),
    DishCategory(21, consts.CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART),
    DishCategory(22, consts.CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART),
]

order_dishes: list[OrderDish] = []
