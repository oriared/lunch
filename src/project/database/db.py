from project.database import models

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
