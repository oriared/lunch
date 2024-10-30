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


def first_dishes() -> list[models.Dish]:
    return db.first_dishes


def get_standard_second_dishes() -> list[models.Dish]:
    return [d for d in db.second_dishes if models.DishCategory(d.id, 3) in db.dish_categories]


def get_constructor_second_dishes(part: str) -> list[models.Dish]:
    if part == 'first':
        return [d for d in db.second_dishes if models.DishCategory(d.id, 4) in db.dish_categories]
    if part == 'second':
        return [d for d in db.second_dishes if models.DishCategory(d.id, 5) in db.dish_categories]
    return []


def get_vegan_dishes() -> list[models.Dish]:
    return [d for d in db.first_dishes if models.DishCategory(d.id, 1) in db.dish_categories]


def save_order(lunch: dto.Lunch, user: dto.User) -> models.Order:
    order_id = len(db.orders) + 1
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
