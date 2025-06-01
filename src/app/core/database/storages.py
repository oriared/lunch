import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core import entities
from core.database import models
from core.dtos import UserCreateOrUpdateDTO


class ObjectDoesNotExistsError(Exception):
    pass


class UserStorage:
    def __init__(self, session: AsyncSession, **kwargs) -> None:  # noqa: ANN003, ARG002
        self.session = session

    @staticmethod
    def model_to_entity(user: models.User) -> entities.User:
        return entities.User(
            id=user.id,
            username=user.username,
            password=user.password,
            name=user.name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            joined_dt=user.joined_dt,
        )

    async def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.User]:
        query = select(models.User).order_by(models.User.id.desc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.scalars(query)
        return [self.model_to_entity(user) for user in result.all()]

    async def get_by_id(self, user_id: int) -> entities.User | None:
        user_model = await self._get_by_id(user_id)
        return self.model_to_entity(user_model) if user_model else None

    async def get_by_username(self, username: str) -> entities.User | None:
        query = select(models.User).where(models.User.username == username)
        user = await self.session.scalar(query)
        return self.model_to_entity(user) if user else None

    async def add(self, user: entities.User, user_data: UserCreateOrUpdateDTO) -> entities.User:
        user_model = models.User(
            id=user.id,
            username=user_data.username,
            password=user_data.password,
            name=user_data.name,
            is_admin=user_data.is_admin,
            is_active=user_data.is_active,
            joined_dt=user_data.joined_dt,
        )
        self.session.add(user_model)
        await self.session.flush()
        return self.model_to_entity(user_model)

    async def update(self, user: entities.User, user_data: UserCreateOrUpdateDTO) -> entities.User:
        user_model = await self._get_by_id(user.id)
        if not user_model:
            raise Exception
        user_model.username = user_data.username
        user_model.password = user_data.password
        user_model.name = user_data.name
        user_model.is_admin = user_data.is_admin
        user_model.is_active = user_data.is_active
        user_model.joined_dt = user_data.joined_dt
        await self.session.flush()
        return self.model_to_entity(user_model)

    async def get_count(self) -> int:
        query = select(func.count(models.User.id))
        return await self.session.scalar(query)

    async def _get_by_id(self, id: int) -> models.User | None:
        query = select(models.User).where(models.User.id == id)
        return await self.session.scalar(query)


class OrderStorage:
    def __init__(self, session: AsyncSession, **kwargs) -> None:  # noqa: ANN003, ARG002
        self.session = session

    @staticmethod
    def model_to_entity(order: models.Order) -> entities.Order:
        return entities.Order(
            id=order.id,
            date=order.date,
            user_id=order.user_id,
            comment=order.comment,
        )

    async def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        query = select(models.Order).order_by(models.Order.date.desc(), models.Order.id.desc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def get_by_id(self, order_id: int) -> entities.Order | None:
        query = select(models.Order).where(models.Order.id == order_id)
        order = await self.session.scalar(query)
        return self.model_to_entity(order) if order else None

    async def get_by_user_id(self, user_id: int, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        query = (
            select(models.Order)
            .where(models.Order.user_id == user_id)
            .order_by(models.Order.date.desc(), models.Order.id.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def get_by_date(self, date: datetime.date, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        query = (
            select(models.Order)
            .where(models.Order.date == date)
            .order_by(models.Order.date.desc(), models.Order.id.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def get_by_user_id_and_date(self, user_id: int, date: datetime.date) -> list[entities.Order]:
        query = (
            select(models.Order)
            .where((models.Order.user_id == user_id) & (models.Order.date == date))
            .order_by(models.Order.date.desc(), models.Order.id.desc())
        )
        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def add(self, order: entities.Order) -> entities.Order:
        order_model = models.Order(
            id=order.id,
            date=order.date,
            user_id=order.user_id,
            comment=order.comment,
        )
        self.session.add(order_model)
        await self.session.flush()
        return self.model_to_entity(order_model)

    async def update(self, order: entities.Order) -> entities.Order:
        order_model = await self._get_by_id(order.id)
        if not order_model:
            raise Exception
        order_model.comment = order.comment
        await self.session.flush()
        return self.model_to_entity(order_model)

    async def delete(self, order: entities.Order) -> None:
        order_model = await self._get_by_id(order.id)
        await self.session.delete(order_model)
        await self.session.flush()

    async def get_count(self) -> int:
        query = select(func.count(models.Order.id))
        return await self.session.scalar(query)

    async def get_user_orders_count(self, user_id: int) -> int:
        query = select(func.count(models.Order.id)).where(models.Order.user_id == user_id)
        return await self.session.scalar(query)

    async def add_dishes(self, order: entities.Order, dishes_ids: list[int]) -> None:
        stmt = models.order_dish.insert().values()
        order_dishes = [{'order_id': order.id, 'dish_id': dish_id} for dish_id in dishes_ids]
        await self.session.execute(stmt, order_dishes)

    async def clear_dishes(self, order: entities.Order) -> None:
        query = select(models.Order).where(models.Order.id == order.id).options(selectinload(models.Order.dishes))
        order_model = await self.session.scalar(query)
        order_model.dishes = []

    async def _get_by_id(self, id: int) -> models.Order | None:
        query = select(models.Order).where(models.Order.id == id)
        return await self.session.scalar(query)


class DishStorage:
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        self.session = kwargs['session']

    @staticmethod
    def model_to_entity(dish: models.Dish) -> entities.Dish:
        return entities.Dish(
            id=dish.id,
            name=dish.name,
            weekday=dish.weekday,
        )

    async def get_by_id(self, dish_id: int) -> entities.Dish | None:
        query = select(models.Dish).where(models.Dish.id == dish_id)
        dish = await self.session.scalar(query)
        return self.model_to_entity(dish) if dish else None

    async def get_by_ids(self, dish_ids: list[int]) -> list[entities.Dish]:
        query = select(models.Dish).where(models.Dish.id.in_(dish_ids)).order_by(models.Dish.id.asc())
        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]

    async def get_by_category_code(self, category_code: str) -> list[entities.Dish]:
        query = (
            select(models.Dish)
            .where(models.Dish.categories.any(models.Category.code == category_code))
            .order_by(models.Dish.id.asc())
        )

        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]

    async def get_by_order_id(self, order_id: int) -> list[entities.Dish]:
        query = (
            select(models.Dish)
            .where(models.Dish.orders.any(models.Order.id == order_id))
            .order_by(models.Dish.id.asc())
        )
        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]

    async def get_by_category_code_and_order_id(self, category_code: str, order_id: int) -> list[entities.Dish]:
        query = (
            select(models.Dish)
            .where(
                and_(
                    models.Dish.categories.any(models.Category.code == category_code),
                    models.Dish.orders.any(models.Order.id == order_id),
                )
            )
            .order_by(models.Dish.id.asc())
        )
        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]
