import datetime

from core import in_memory_db, entities


class ObjectDoesNotExistsError(Exception):
    pass


class UserInMemoryStorage:
    def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.User]:
        users = sorted(in_memory_db.users, key=lambda user: user.joined_dt, reverse=True)
        if limit is None:
            return users
        return users[offset : offset + limit]

    def get_by_id(self, user_id: int) -> entities.User | None:
        for user in in_memory_db.users:
            if user.id == user_id:
                break
        else:
            return None
        return user

    def get_by_username(self, username: str) -> entities.User | None:
        for user in in_memory_db.users:
            if user.username == username:
                break
        else:
            return None
        return user

    def add(self, user: entities.User) -> entities.User:
        user.id = max([user.id for user in in_memory_db.users], default=0) + 1
        in_memory_db.users.append(user)
        return user

    def update(self, user: entities.User) -> entities.User:
        user_from_db = self.get_by_id(user.id)
        if not user_from_db:
            raise ObjectDoesNotExistsError
        user_from_db.username = user.username
        user_from_db.password = user.password
        user_from_db.name = user.name
        user_from_db.is_admin = user.is_admin

        return user_from_db

    def get_count(self, **kwargs: str | int | None) -> int:
        users = in_memory_db.users
        for key, value in kwargs.items():
            users = [user for user in users if getattr(user, key) == value]
        return len(users)


class OrderInMemoryStorage:
    def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        orders = sorted(in_memory_db.orders, key=lambda order: order.date, reverse=True)
        if limit is None:
            return orders
        return orders[offset : offset + limit]

    def get_by_id(self, order_id: int) -> entities.Order | None:
        for order in in_memory_db.orders:
            if order.id == order_id:
                break
        else:
            return None
        return order

    def get_by_user_id(self, user_id: int, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        user_orders = [order for order in in_memory_db.orders if order.user_id == user_id]
        sorted_user_orders = sorted(user_orders, key=lambda order: order.date, reverse=True)
        if limit is None:
            return sorted_user_orders
        return sorted_user_orders[offset : offset + limit]

    def get_by_date(self, date: datetime.date, offset: int = 0, limit: int | None = None) -> list[entities.Order]:
        date_orders = [order for order in in_memory_db.orders if order.date == date]
        sorted_date_orders = sorted(date_orders, key=lambda order: order.date, reverse=True)
        if limit is None:
            return sorted_date_orders
        return sorted_date_orders[offset : offset + limit]

    def get_by_user_id_and_date(self, user_id: int, date: datetime.date) -> list[entities.Order]:
        user_date_orders = [order for order in in_memory_db.orders if order.user_id == user_id and order.date == date]
        return sorted(user_date_orders, key=lambda order: order.date, reverse=True)

    def add(self, order: entities.Order) -> entities.Order:
        order.id = max([order.id for order in in_memory_db.orders], default=0) + 1
        in_memory_db.orders.append(order)
        return order

    def update(self, order: entities.Order) -> entities.Order:
        order_from_db = self.get_by_id(order.id)
        if not order_from_db:
            raise ObjectDoesNotExistsError
        order_from_db.date = order.date
        order_from_db.comment = order.comment

        return order_from_db

    def delete(self, order: entities.Order) -> None:
        order_from_db = self.get_by_id(order.id)
        if not order_from_db:
            raise ObjectDoesNotExistsError
        in_memory_db.orders.remove(order_from_db)

    def get_count(self, **kwargs: str | int | None) -> int:
        orders = in_memory_db.orders
        for key, value in kwargs.items():
            orders = [order for order in orders if getattr(order, key) == value]
        return len(orders)

    def add_dishes(self, order: entities.Order, dishes: list[entities.Dish]) -> None:
        for dish in dishes:
            order_dish = in_memory_db.OrderDish(order_id=order.id, dish_id=dish.id)
            in_memory_db.order_dishes.append(order_dish)

    def clear_dishes(self, order: entities.Order) -> None:
        for order_dish in in_memory_db.order_dishes:
            if order_dish.order_id == order.id:
                in_memory_db.order_dishes.remove(order_dish)


class DishInMemoryStorage:
    def get_all(self, offset: int = 0, limit: int | None = None) -> list[entities.Dish]:
        if limit is None:
            return in_memory_db.dishes
        return in_memory_db.dishes[offset : offset + limit]

    def get_by_id(self, dish_id: int) -> entities.Dish | None:
        for dish in in_memory_db.dishes:
            if dish.id == dish_id:
                break
        else:
            return None
        return dish

    def get_by_ids(self, dish_ids: list[int]) -> list[entities.Dish]:
        return [dish for dish in in_memory_db.dishes if dish.id in dish_ids]

    def get_by_category_code(self, category_code: str, date: datetime.date | None = None) -> list[entities.Dish]:
        dishes_ids = [
            dish_category.dish_id
            for dish_category in in_memory_db.dishes_categories
            if dish_category.category_code == category_code
        ]
        dishes = [self.get_by_id(dish_id) for dish_id in dishes_ids]
        if date is None:
            return dishes
        return [dish for dish in dishes if not dish.weekday or dish.weekday == date.isoweekday()]

    def get_by_order_id(self, order_id: int) -> list[entities.Dish]:
        dishes_ids = [order_dish.dish_id for order_dish in in_memory_db.order_dishes if order_dish.order_id == order_id]
        return [self.get_by_id(dish_id) for dish_id in dishes_ids]

    def get_by_category_code_and_order_id(self, category_code: str, order_id: int) -> list[entities.Dish]:
        dishes_by_order = self.get_by_order_id(order_id=order_id)
        dishes_by_category = self.get_by_category_code(category_code=category_code)
        return [dish for dish in dishes_by_order if dish in dishes_by_category]
