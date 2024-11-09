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


def get_users() -> list[models.User]:
    return db.users


def get_user_orders(user: dto.User) -> list[models.Order]:
    return [order for order in db.orders if order.user_id == user.id]


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


def get_first_dishes() -> list[models.Dish]:
    return db.first_dishes


def get_standard_second_dishes() -> list[models.Dish]:
    return [d for d in db.second_dishes if models.DishCategory(d.id, 3) in db.dish_categories]


def get_constructor_second_dishes(part: str | None = None) -> list[models.Dish]:
    if part == 'first':
        return [d for d in db.second_dishes if models.DishCategory(d.id, 4) in db.dish_categories]
    if part == 'second':
        return [d for d in db.second_dishes if models.DishCategory(d.id, 5) in db.dish_categories]
    return get_constructor_second_dishes(part='first') + get_constructor_second_dishes(part='second')


def get_vegan_dishes() -> list[models.Dish]:
    return [d for d in db.first_dishes if models.DishCategory(d.id, 1) in db.dish_categories]


def get_order(date: datetime.date, user: dto.User) -> models.Order:
    return get_orders_by_date(date=date, orders=get_user_orders(user=user))[0]


def save_order(lunch: dto.Lunch, user: dto.User) -> models.Order:
    user_orders = get_orders_by_date(date=lunch.date, orders=get_user_orders(user=user))
    if user_orders:
        delete_order(order=user_orders[0])

    order_id = max([order.id for order in db.orders], default=0) + 1
    dishes_text = get_lunch_dishes_text(lunch=lunch)

    order = models.Order(id=order_id, user_id=user.id, date=lunch.date, dishes_text=dishes_text, comment=lunch.comment)
    db.orders.append(order)

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
    return order


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
