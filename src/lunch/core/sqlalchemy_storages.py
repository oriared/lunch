import datetime

from sqlalchemy import and_, func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core import entities, sqlalchemy_db


class ObjectDoesNotExistsError(Exception):
    pass


class UserSQLAlchemyStorage:
    def __init__(self, session: AsyncSession, **kwargs) -> None:  # noqa: ANN003, ARG002
        self.session = session

    @staticmethod
    def model_to_entity(user: sqlalchemy_db.User) -> entities.User:
        return entities.User(
            id=user.id,
            username=user.username,
            password=user.password,
            name=user.name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            joined_dt=user.joined_dt,
        )

    @staticmethod
    def entity_to_model(user: entities.User) -> sqlalchemy_db.User:
        return sqlalchemy_db.User(
            id=user.id,
            username=user.username,
            password=user.password,
            name=user.name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            joined_dt=user.joined_dt,
        )

    async def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.User]:
        query = select(sqlalchemy_db.User)
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
        query = select(sqlalchemy_db.User).where(sqlalchemy_db.User.username == username)
        user = await self.session.scalar(query)
        return self.model_to_entity(user) if user else None

    async def add(self, user: entities.User) -> entities.User:
        user_model = self.entity_to_model(user)
        self.session.add(user_model)
        await self.session.flush()
        return self.model_to_entity(user_model)

    async def update(self, user: entities.User) -> entities.User:
        user_model = await self._get_by_id(user.id)
        if not user_model:
            raise Exception
        user_model.username = user.username
        user_model.password = user.password
        user_model.name = user.name
        user_model.is_admin = user.is_admin
        user_model.is_active = user.is_active
        user_model.joined_dt = user.joined_dt
        await self.session.flush()
        return self.model_to_entity(user_model)

    async def get_count(self) -> int:
        query = select(func.count(sqlalchemy_db.User.id))
        return await self.session.scalar(query)

    async def _get_by_id(self, id: int) -> sqlalchemy_db.User | None:
        query = select(sqlalchemy_db.User).where(sqlalchemy_db.User.id == id)
        return await self.session.scalar(query)


class OrderSQLAlchemyStorage:
    def __init__(self, session: AsyncSession, **kwargs) -> None:  # noqa: ANN003, ARG002
        self.session = session

    @staticmethod
    def model_to_entity(order: sqlalchemy_db.Order) -> entities.Order:
        return entities.Order(
            id=order.id,
            date=order.date,
            user_id=order.user_id,
            comment=order.comment,
        )

    @staticmethod
    def entity_to_model(order: entities.Order) -> sqlalchemy_db.Order:
        return sqlalchemy_db.Order(
            id=order.id,
            date=order.date,
            user_id=order.user_id,
            comment=order.comment,
        )

    async def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        query = select(sqlalchemy_db.Order)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def get_by_id(self, order_id: int) -> entities.Order | None:
        query = select(sqlalchemy_db.Order).where(sqlalchemy_db.Order.id == order_id)
        order = await self.session.scalar(query)
        return self.model_to_entity(order) if order else None

    async def get_by_user_id(self, user_id: int, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        query = select(sqlalchemy_db.Order).where(sqlalchemy_db.Order.user_id == user_id)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def get_by_date(self, date: datetime.date, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        query = select(sqlalchemy_db.Order).where(sqlalchemy_db.Order.date == date)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def get_by_user_id_and_date(self, user_id: int, date: datetime.date) -> list[entities.Order]:
        query = select(sqlalchemy_db.Order).where(
            (sqlalchemy_db.Order.user_id == user_id) & (sqlalchemy_db.Order.date == date)
        )
        result = await self.session.scalars(query)
        return [self.model_to_entity(order) for order in result.all()]

    async def add(self, order: entities.Order) -> entities.Order:
        order_model = self.entity_to_model(order)
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

    async def get_count(self) -> int:
        query = select(func.count(sqlalchemy_db.User.id))
        return await self.session.scalar(query)

    async def get_user_orders_count(self, user_id: int) -> int:
        query = select(func.count(sqlalchemy_db.Order.id)).where(sqlalchemy_db.Order.user_id == user_id)
        return await self.session.scalar(query)

    async def add_dishes(self, order: entities.Order, dishes_ids: list[int]) -> None:
        stmt = sqlalchemy_db.order_dish.insert().values()
        order_dishes = [{'order_id': order.id, 'dish_id': dish_id} for dish_id in dishes_ids]
        await self.session.execute(stmt, order_dishes)

    async def clear_dishes(self, order: entities.Order) -> None:
        stmt = sqlalchemy_db.order_dish.delete().where(sqlalchemy_db.order_dish.order_id == order.id)
        await self.session.execute(stmt)

    async def _get_by_id(self, id: int) -> sqlalchemy_db.Order | None:
        query = select(sqlalchemy_db.Order).where(sqlalchemy_db.Order.id == id)
        return await self.session.scalar(query)


class DishSQLAlchemyStorage:
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        self.session = kwargs['session']

    @staticmethod
    def model_to_entity(dish: sqlalchemy_db.Dish) -> entities.Dish:
        return entities.Dish(
            id=dish.id,
            name=dish.name,
            weekday=dish.weekday,
        )

    @staticmethod
    def entity_to_model(dish: entities.Dish) -> sqlalchemy_db.Dish:
        return sqlalchemy_db.Dish(
            id=dish.id,
            name=dish.name,
            weekday=dish.weekday,
        )

    async def get_by_id(self, dish_id: int) -> entities.Dish | None:
        query = select(sqlalchemy_db.Dish).where(sqlalchemy_db.Dish.id == dish_id)
        dish = await self.session.scalar(query)
        return self.model_to_entity(dish) if dish else None

    async def get_by_ids(self, dish_ids: list[int]) -> list[entities.Dish]:
        query = select(sqlalchemy_db.Dish).where(sqlalchemy_db.Dish.id.in_(dish_ids))
        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]

    async def get_by_category_code(self, category_code: str, date: datetime.date | None = None) -> list[entities.Dish]:
        query = select(sqlalchemy_db.Dish).where(
            sqlalchemy_db.Dish.categories.any(sqlalchemy_db.Category.code == category_code)
        )
        if date:
            weekday = date.isoweekday()
            query = query.where(or_(sqlalchemy_db.Dish.weekday == weekday, sqlalchemy_db.Dish.weekday == ''))

        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]

    async def get_by_order_id(self, order_id: int) -> list[entities.Dish]:
        query = select(sqlalchemy_db.Dish).where(sqlalchemy_db.Dish.orders.any(sqlalchemy_db.Order.id == order_id))
        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]

    async def get_by_category_code_and_order_id(self, category_code: str, order_id: int) -> list[entities.Dish]:
        query = select(sqlalchemy_db.Dish).where(
            and_(
                sqlalchemy_db.Dish.categories.any(sqlalchemy_db.Category.code == category_code),
                sqlalchemy_db.Dish.orders.any(sqlalchemy_db.Order.id == order_id),
            )
        )
        dishes = await self.session.scalars(query)
        return [self.model_to_entity(dish) for dish in dishes.all()]
