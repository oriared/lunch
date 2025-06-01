import datetime

from core import entities
from core.consts import CategoryCode
from core.database.storages import DishStorage, OrderStorage, UserStorage
from core.dtos import UserCreateOrUpdateDTO


class UserRepo:
    def __init__(self, user: entities.User | None = None, **kwargs) -> None:  # noqa: ANN003
        self.user = user
        self.storage = UserStorage(session=kwargs['session'])

    class UserNotFoundError(Exception):
        pass

    async def get_all(self, page: int | None = None, per_page: int | None = None) -> list[entities.User]:
        offset = (page - 1) * per_page
        return await self.storage.get_all(offset=offset, limit=per_page)

    async def get_by_id(self, user_id: int) -> entities.User | None:
        return await self.storage.get_by_id(user_id=user_id)

    async def get_by_username(self, username: str) -> entities.User | None:
        return await self.storage.get_by_username(username=username)

    async def save(self, user_data: UserCreateOrUpdateDTO) -> entities.User:
        if self.user.id is None:
            self.user = await self.storage.add(self.user, user_data)
        else:
            self.user = await self.storage.update(self.user, user_data)
        return self.user

    async def get_count(self) -> int:
        return await self.storage.get_count()


class OrderRepo:
    def __init__(self, order: entities.Order | None = None, **kwargs) -> None:  # noqa: ANN003
        self.order = order
        self.storage = OrderStorage(session=kwargs['session'])

    class OrderNotFoundError(Exception):
        pass

    async def get_by_id(self, order_id: int) -> entities.Order:
        return await self.storage.get_by_id(order_id=order_id)

    async def get_all(self, page: int | None = None, per_page: int | None = None) -> list[entities.Order]:
        offset = (page - 1) * per_page
        return await self.storage.get_all(offset=offset, limit=per_page)

    async def get_by_date(self, date: datetime.date) -> list[entities.Order]:
        return await self.storage.get_by_date(date=date)

    async def get_by_user_id(
        self, user_id: int, page: int | None = None, per_page: int | None = None
    ) -> list[entities.Order]:
        offset = (page - 1) * per_page
        return await self.storage.get_by_user_id(user_id=user_id, offset=offset, limit=per_page)

    async def get_by_user_id_and_date(self, user_id: int, date: datetime.date) -> list[entities.Order]:
        return await self.storage.get_by_user_id_and_date(user_id=user_id, date=date)

    async def save(self) -> entities.Order:
        if self.order.id is None:
            self.order = await self.storage.add(self.order)
        else:
            self.order = await self.storage.update(self.order)
        return self.order

    async def delete(self) -> None:
        if not self.order:
            raise self.OrderNotFoundError()
        await self.storage.delete(order=self.order)

    async def get_count(self) -> int:
        return await self.storage.get_count()

    async def get_user_orders_count(self, user_id: int) -> int:
        return await self.storage.get_user_orders_count(user_id=user_id)

    async def add_dishes(self, dishes_ids: list[int]) -> None:
        if not self.order:
            raise self.OrderNotFoundError()
        await self.storage.add_dishes(order=self.order, dishes_ids=dishes_ids)

    async def clear_dishes(self) -> None:
        if not self.order:
            raise self.OrderNotFoundError()
        await self.storage.clear_dishes(order=self.order)


class DishRepo:
    def __init__(self, dish: entities.Dish | None = None, **kwargs) -> None:  # noqa ANN003, ARG002
        self.dish = dish
        self.storage = DishStorage(session=kwargs['session'])

    class DishNotFoundError(Exception):
        pass

    async def get_by_id(self, dish_id: int) -> entities.Dish | None:
        return await self.storage.get_by_id(dish_id=dish_id)

    async def get_by_ids(self, dish_ids: list[int]) -> list[entities.Dish]:
        return await self.storage.get_by_ids(dish_ids=dish_ids)

    async def get_first_dishes(self) -> list[entities.Dish]:
        return await self.storage.get_by_category_code(category_code=CategoryCode.FIRST)

    async def get_vegan_dishes(self) -> list[entities.Dish]:
        return await self.storage.get_by_category_code(category_code=CategoryCode.VEGAN)

    async def get_standard_second_dishes(self) -> list[entities.Dish]:
        return await self.storage.get_by_category_code(category_code=CategoryCode.SECOND_STANDARD)

    async def get_constructor_second_dishes_first_part(self) -> list[entities.Dish]:
        return await self.storage.get_by_category_code(category_code=CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART)

    async def get_constructor_second_dishes_second_part(self) -> list[entities.Dish]:
        return await self.storage.get_by_category_code(category_code=CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART)

    async def get_by_order_id(self, order_id: int) -> list[entities.Dish]:
        return await self.storage.get_by_order_id(order_id=order_id)

    async def get_order_first_dish(self, order_id: int) -> entities.Dish | None:
        order_first_dishes = await self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.FIRST, order_id=order_id
        )
        if not order_first_dishes:
            return None
        return order_first_dishes[0]

    async def get_order_second_dish(self, order_id: int) -> entities.Dish | None:
        order_second_dishes = await self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.SECOND_STANDARD, order_id=order_id
        )
        if not order_second_dishes:
            return None
        return order_second_dishes[0]

    async def get_order_second_dish_first_part(self, order_id: int) -> entities.Dish | None:
        order_second_dish_first_part = await self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.SECOND_CONSTRUCTOR_MAIN_PART, order_id=order_id
        )
        if not order_second_dish_first_part:
            return None
        return order_second_dish_first_part[0]

    async def get_order_second_dish_second_part(self, order_id: int) -> entities.Dish | None:
        order_second_dish_second_part = await self.storage.get_by_category_code_and_order_id(
            category_code=CategoryCode.SECOND_CONSTRUCTOR_SIDE_PART, order_id=order_id
        )
        if not order_second_dish_second_part:
            return None
        return order_second_dish_second_part[0]
