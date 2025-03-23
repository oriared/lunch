import datetime
from typing import TYPE_CHECKING, Any

from core import entities
from core.consts import DishMode
from core.interactors import DishManager, UserManager

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection


async def retrieve_user_handler(
    session: dict[str, Any],
    connection: 'ASGIConnection[Any, Any, Any, Any]',  # noqa: ARG001
) -> entities.User | None:
    user_id = session.get('user_id')
    return UserManager().get_by_id(user_id=user_id) if user_id else None


def check_password(user: entities.User, password: str) -> bool:
    return user.password == password


def get_order_date_choices() -> list[datetime.date]:
    """Даты, на которые можно заказать обед."""
    return get_dates_from_tomorrow_to_weekends() or get_next_week_work_days()


def get_dates_from_tomorrow_to_weekends() -> list[datetime.date]:
    """Даты начиная с завтрашней и до пятницы текущей недели включительно."""
    saturday_iso = 6
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    from_tomorrow_to_weekend = saturday_iso - tomorrow.isoweekday()

    return [tomorrow + datetime.timedelta(days=index) for index in range(from_tomorrow_to_weekend)]


def get_next_week_work_days() -> list[datetime.date]:
    """Будни следующей недели."""
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    next_monday = tomorrow + datetime.timedelta(days=7 - today.isoweekday())

    return [next_monday + datetime.timedelta(days=day_index) for day_index in range(5)]


def get_next_work_day() -> datetime.date:
    today_iso = datetime.date.today().isoweekday()
    saturday_iso = 6
    if today_iso + 1 < saturday_iso:
        return datetime.date.today() + datetime.timedelta(days=1)
    return datetime.date.today() + datetime.timedelta(days=7 - today_iso)


def get_dish_mode(dish: entities.Dish) -> str:
    if dish in DishManager().get_standard_second_dishes():
        return DishMode.STANDARD

    return DishMode.CONSTRUCTOR


def validate_user_data(data: dict[str, Any], user: entities.User | None = None) -> tuple[bool, dict[str, str]]:
    errors = {}
    required_fields = ['username', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            errors[field] = 'Обязательное поле'

    if data.get('username'):
        user_with_same_username = UserManager().get_by_username(username=data['username'])
        if user_with_same_username and user_with_same_username != user:
            errors['username'] = 'Такой пользователь уже существует'

    if data.get('password') and len(data['password']) < 4:
        errors['password'] = 'Минимальная длина пароля 4 символа'  # noqa: S105

    if data.get('name') and len(data['name']) < 3:
        errors['name'] = 'Минимальная длина имени 3 символа'

    return bool(not errors), errors
