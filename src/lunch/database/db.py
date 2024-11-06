import datetime

from database import models

users = [
    models.User(1, 'admin', 'admin', datetime.datetime(2024, 10, 20, 10, 47), is_admin=True),
    models.User(2, 'iar', 'admin', datetime.datetime(2024, 10, 20, 10, 30), is_admin=False, name='Ярослав Орлов'),
    models.User(3, 'abandoned', 'admin', datetime.datetime(2024, 10, 16, 14, 15), is_admin=False),
    models.User(4, 'dzhamil', 'admin', datetime.datetime(2024, 10, 14, 20, 22), is_admin=False, name='Джамиль'),
]

first_dishes = [
    models.Dish(1, 'Котлета'),
    models.Dish(2, 'Рыба'),
    models.Dish(3, 'Стейк'),
    models.Dish(4, 'Курица'),
    models.Dish(5, 'Салат'),
    models.Dish(6, 'Суп грибной'),
]

second_dishes = [
    models.Dish(7, 'Удон с креветками'),
    models.Dish(8, 'Соба с говядиной'),
    models.Dish(9, 'Пельмени жареные'),
    models.Dish(10, 'Курица по-французски'),
    models.Dish(11, 'Кебаб куриный'),
    models.Dish(12, 'Пюре картофельное'),
    models.Dish(13, 'Картошка печёная'),
    models.Dish(14, 'Булгур с овощами'),
]

dishes = first_dishes + second_dishes

categories = [
    models.Category(1, 'Веган', None),
    models.Category(2, 'Вторые блюда', None),
    models.Category(3, 'Стандарт', 2),
    models.Category(4, 'Конструктор первая часть', 2),
    models.Category(5, 'Конструктор вторая часть', 2),
]

dish_categories = [
    models.DishCategory(5, 1),
    models.DishCategory(6, 1),
    models.DishCategory(7, 3),
    models.DishCategory(8, 3),
    models.DishCategory(9, 3),
    models.DishCategory(10, 4),
    models.DishCategory(11, 4),
    models.DishCategory(12, 5),
    models.DishCategory(13, 5),
    models.DishCategory(14, 5),
]

orders = []

order_dishes = []
