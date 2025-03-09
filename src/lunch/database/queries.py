import datetime

import consts
import dto

from database import db, models


class ObjectDoesNotExistsError(Exception):
    pass


def get_user_by_username(username: str) -> dto.User | None:
    for user in db.users:
        if user.username == username:
            break
    else:
        return None
    return user


def get_user_by_id(user_id: int) -> dto.User | None:
    for user in db.users:
        if user.id == user_id:
            break
    else:
        return None
    return user


def get_users(page: int | None = None) -> list[models.User]:
    sorted_users = sort_users_by_dt_joined(db.users)
    if not page:
        return sorted_users
    return sorted_users[consts.ITEMS_PER_PAGE * (page - 1) : consts.ITEMS_PER_PAGE * page]


def sort_users_by_dt_joined(users: list[models.User]) -> list[models.User]:
    return sorted(users, key=lambda user: user.joined_dt, reverse=True)


def create_user(user_data: dict) -> models.User:
    user_id = max([user.id for user in db.users], default=0) + 1
    user = models.User(
        id=user_id,
        username=user_data['username'],
        password=user_data['password'],
        name=user_data['name'],
        is_admin=user_data['is_admin'],
        joined_dt=datetime.datetime.now(),
    )
    db.users.append(user)
    return user


def update_user(user: models.User, user_data: dict) -> models.User:
    user.username = user_data['username']
    user.password = user_data['password']
    user.name = user_data['name']
    user.is_admin = user_data['is_admin']

    return user


def get_user_orders(user: dto.User, page: int | None = None) -> list[models.Order]:
    all_user_orders = [order for order in db.orders if order.user_id == user.id]
    sorted_orders = sort_orders_by_date(all_user_orders)
    if not page:
        return sorted_orders
    return sorted_orders[consts.ITEMS_PER_PAGE * (page - 1) : consts.ITEMS_PER_PAGE * page]


def sort_orders_by_date(orders: list[models.Order]) -> list[models.Order]:
    return sorted(orders, key=lambda order: order.date, reverse=True)


def get_user_order_by_date(user: dto.User, date: datetime.date) -> models.Order | None:
    for order in db.orders:
        if order.user_id == user.id and order.date == date:
            return order
    return None


def get_orders_by_date(date: datetime.date, orders: list[models.Order] | None = None) -> list[models.Order]:
    if orders is None:
        orders = db.orders
    return [order for order in orders if order.date == date]


def get_order_dishes(order: models.Order) -> list[models.Dish]:
    return [get_dish(dish_id=od.dish_id) for od in db.order_dishes if od.order_id == order.id]


def get_order_first_dish(order: models.Order) -> models.Dish | None:
    dishes = get_order_dishes(order=order)
    for dish in dishes:
        if dish in get_first_dishes():
            return dish
    return None


def get_order_second_dish(order: models.Order) -> models.Dish | None:
    dishes = get_order_dishes(order=order)
    for dish in dishes:
        if dish in get_standard_second_dishes():
            return dish
    return None


def get_order_second_dish_first_part(order: models.Order) -> models.Dish | None:
    dishes_ids = [dish.id for dish in get_order_dishes(order=order)]
    second_dish_first_part_ids = [dc.dish_id for dc in db.dish_categories if dc.category_id in (2, 4)]
    for dish_id in dishes_ids:
        if dish_id in second_dish_first_part_ids:
            return get_dish(dish_id)
    return None


def get_order_second_dish_second_part(order: models.Order) -> models.Dish | None:
    dishes_ids = [dish.id for dish in get_order_dishes(order=order)]
    second_dish_second_part_ids = [dc.dish_id for dc in db.dish_categories if dc.category_id == 5]
    for dish_id in dishes_ids:
        if dish_id in second_dish_second_part_ids:
            return get_dish(dish_id)
    return None


def get_first_dishes(date: datetime.date | None = None) -> list[models.Dish]:
    if not date:
        return db.first_dishes
    today_weekday = date.isoweekday()
    return [d for d in db.first_dishes if not d.weekday or d.weekday == today_weekday]


def get_standard_second_dishes(date: datetime.date | None = None) -> list[models.Dish]:
    second_dishes = [d for d in db.second_dishes if models.DishCategory(d.id, 3) in db.dish_categories]
    if not date:
        return second_dishes
    today_weekday = date.isoweekday()
    return [d for d in second_dishes if not d.weekday or d.weekday == today_weekday]


def get_constructor_second_dishes(part: str | None = None, date: datetime.date | None = None) -> list[models.Dish]:
    assert part in ('first', 'second', None)  # noqa S101
    if part == 'first':
        second_dishes = [d for d in db.second_dishes if models.DishCategory(d.id, 4) in db.dish_categories]
    elif part == 'second':
        second_dishes = [d for d in db.second_dishes if models.DishCategory(d.id, 5) in db.dish_categories]
    else:
        second_dishes = get_constructor_second_dishes(part='first', date=date) + get_constructor_second_dishes(
            part='second', date=date
        )
    if not date:
        return second_dishes
    today_weekday = date.isoweekday()
    return [d for d in second_dishes if not d.weekday or d.weekday == today_weekday]


def get_vegan_dishes(date: datetime.date | None = None) -> list[models.Dish]:
    all_vegan_dishes = [d for d in db.first_dishes if models.DishCategory(d.id, 1) in db.dish_categories]
    if not date:
        return all_vegan_dishes
    today_weekday = date.isoweekday()
    return [d for d in all_vegan_dishes if not d.weekday or d.weekday == today_weekday]


def get_orders(page: int | None = None) -> list[models.Order]:
    all_orders = db.orders
    sorted_orders = sort_orders_by_date(all_orders)
    if page is None:
        return sorted_orders
    return sorted_orders[consts.ITEMS_PER_PAGE * (page - 1) : consts.ITEMS_PER_PAGE * page]


def get_order(order_id: int) -> models.Order:
    try:
        return next(order for order in db.orders if order.id == order_id)
    except IndexError as e:
        raise ObjectDoesNotExistsError from e


def create_order(lunch: dto.Lunch, user: dto.User | None) -> models.Order:
    order_id = max([order.id for order in db.orders], default=0) + 1
    dishes_text = get_lunch_dishes_text(lunch=lunch)

    user_id = user.id if user else None

    order = models.Order(id=order_id, user_id=user_id, date=lunch.date, dishes_text=dishes_text, comment=lunch.comment)
    db.orders.append(order)

    save_order_dishes(order=order, lunch=lunch)
    return order


def update_order(order: models.Order, lunch: dto.Lunch) -> models.Order:
    order.dishes_text = get_lunch_dishes_text(lunch=lunch)
    order.comment = lunch.comment
    save_order_dishes(order=order, lunch=lunch)
    return order


def save_order_dishes(order: models.Order, lunch: dto.Lunch) -> None:
    if lunch.first_dish:
        order_first_dish = models.OrderDish(order_id=order.id, dish_id=int(lunch.first_dish), count=1)
        db.order_dishes.append(order_first_dish)
    if lunch.second_dish_first_part:
        order_second_dish_first_part = models.OrderDish(
            order_id=order.id,
            dish_id=int(lunch.second_dish_first_part),
            count=1,
        )
        db.order_dishes.append(order_second_dish_first_part)
    if lunch.dish_mode == consts.DishMode.CONSTRUCTOR and lunch.second_dish_second_part:
        order_second_dish_second_part = models.OrderDish(
            order_id=order.id,
            dish_id=int(lunch.second_dish_second_part),
            count=1,
        )
        db.order_dishes.append(order_second_dish_second_part)


def get_lunch_dishes_text(lunch: dto.Lunch) -> str:
    dishes_ids = [i for i in (lunch.first_dish, lunch.second_dish_first_part, lunch.second_dish_second_part) if i]
    dishes = [get_dish(dish_id=int(i)) for i in dishes_ids]
    return ', '.join([dish.name for dish in dishes]).capitalize()


def get_dish(dish_id: int) -> models.Dish:
    for dish in db.dishes:
        if dish.id == dish_id:
            break
    else:
        raise ObjectDoesNotExistsError
    return dish


def delete_order(order: models.Order) -> None:
    db.orders.remove(order)
