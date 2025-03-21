import datetime

from core import entities
from core.consts import CategoryCode
from core.storages import DishInMemoryStorage, OrderInMemoryStorage, UserInMemoryStorage


class UserManager:
    def __init__(self, user: entities.User | None = None) -> None:
        self.user = user
        self.storage = UserInMemoryStorage()

    def get_all(self, page: int | None = None, per_page: int | None = None) -> list[entities.User]:
        offset = (page - 1) * per_page
        return self.storage.get_all(offset=offset, limit=per_page)

    def get_by_id(self, user_id: int) -> entities.User | None:
        return self.storage.get_by_id(user_id=user_id)

    def get_by_username(self, username: str) -> entities.User | None:
        return self.storage.get_by_username(username=username)

    def save(self) -> entities.User:
        if self.user.id is None:
            self.user = self.storage.add(self.user)
        else:
            self.user = self.storage.update(self.user)
        return self.user

    def get_count(self, **kwargs: str | int | None) -> int:
        return self.storage.get_count(**kwargs)


class OrderManager:
    def __init__(self, order: entities.Order | None = None) -> None:
        self.order = order
        self.storage = OrderInMemoryStorage()

    def get_by_id(self, order_id: int) -> entities.Order:
        return self.storage.get_by_id(order_id=order_id)

    def get_all(self, page: int | None = None, per_page: int | None = None) -> list[entities.Order]:
        offset = (page - 1) * per_page
        return self.storage.get_all(offset=offset, limit=per_page)

    def get_by_date(self, date: datetime.date) -> list[entities.Order]:
        return self.storage.get_by_date(date=date)

    def get_by_user_id(
        self, user_id: int, page: int | None = None, per_page: int | None = None
    ) -> list[entities.Order]:
        offset = (page - 1) * per_page
        return self.storage.get_by_user_id(user_id=user_id, offset=offset, limit=per_page)

    def get_by_user_id_and_date(self, user_id: int, date: datetime.date) -> list[entities.Order]:
        return self.storage.get_by_user_id_and_date(user_id=user_id, date=date)

    def save(self) -> entities.Order:
        if self.order.id is None:
            self.order = self.storage.add(self.order)
        else:
            self.order = self.storage.update(self.order)
        return self.order

    def delete(self) -> None:
        self.storage.delete(order=self.order)

    def get_count(self, **kwargs: str | int | None) -> int:
        return self.storage.get_count(**kwargs)

    def add_dishes(self, dishes: list[entities.Dish]) -> None:
        self.storage.add_dishes(order=self.order, dishes=dishes)

    def clear_dishes(self) -> None:
        self.storage.clear_dishes(order=self.order)


class DishManager:
    def __init__(self, dish: entities.Dish | None = None) -> None:
        self.dish = dish
        self.storage = DishInMemoryStorage()

    def get_by_id(self, dish_id: int) -> entities.Dish | None:
        return self.storage.get_by_id(dish_id=dish_id)

    def get_by_ids(self, dish_ids: list[int]) -> list[entities.Dish]:
        return self.storage.get_by_ids(dish_ids=dish_ids)

    def get_first_dishes(self, date: datetime.date | None = None) -> list[entities.Dish]:
        return self.storage.get_by_category_code(category_code=CategoryCode.FIRST, date=date)

    def get_vegan_dishes(self, date: datetime.date | None = None) -> list[entities.Dish]:
        return self.storage.get_by_category_code(category_code=CategoryCode.VEGAN, date=date)

    def get_standard_second_dishes(self, date: datetime.date | None = None) -> list[entities.Dish]:
        return self.storage.get_by_category_code(category_code=CategoryCode.SECOND_STANDARD, date=date)

    def get_constructor_second_dishes_first_part(self, date: datetime.date | None = None) -> list[entities.Dish]:
        return self.storage.get_by_category_code(category_code=CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART, date=date)

    def get_constructor_second_dishes_second_part(self, date: datetime.date | None = None) -> list[entities.Dish]:
        return self.storage.get_by_category_code(category_code=CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART, date=date)

    def get_by_order_id(self, order_id: int) -> list[entities.Dish]:
        return self.storage.get_by_order_id(order_id=order_id)

    def get_order_first_dish(self, order_id: int) -> entities.Dish | None:
        order_first_dishes = self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.FIRST, order_id=order_id
        )
        if not order_first_dishes:
            return None
        return order_first_dishes[0]

    def get_order_second_dish(self, order_id: int) -> entities.Dish | None:
        order_second_dishes = self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.SECOND_STANDARD, order_id=order_id
        )
        if not order_second_dishes:
            return None
        return order_second_dishes[0]

    def get_order_second_dish_first_part(self, order_id: int) -> entities.Dish | None:
        order_second_dish_first_part = self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART, order_id=order_id
        )
        if not order_second_dish_first_part:
            return None
        return order_second_dish_first_part[0]

    def get_order_second_dish_second_part(self, order_id: int) -> entities.Dish | None:
        order_second_dish_second_part = self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART, order_id=order_id
        )
        if not order_second_dish_second_part:
            return None
        return order_second_dish_second_part[0]
