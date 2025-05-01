import datetime


class DishMode:
    """
    Стандарт - стандартное первое и стандартное второе блюда
    Конструктор - стандартное первое блюдо и второе блюдо собираемое из двух частей (горячее + гарнир)
    """

    STANDARD = 'STANDARD'
    CONSTRUCTOR = 'CONSTRUCTOR'


class CategoryCode:
    FIRST = 'FIRST'
    SECOND_STANDARD = 'SECOND_STANDARD'
    SECOND_CONSTRUCTOR_MAIN_PART = 'SECOND_CONSTRUCTOR_MAIN_PART'
    SECOND_CONSTRUCTOR_SIDE_PART = 'SECOND_CONSTRUCTOR_SIDE_PART'
    VEGAN = 'VEGAN'


# Время после которого создание и редактирование заказов на завтра невозможно
DEADLINE_TIME = datetime.time(19, 00, 00)
