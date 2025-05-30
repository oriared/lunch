import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core import entities
from core.consts import DEADLINE_TIME, DishMode
from core.interactors import DishManager


def check_password(user: entities.User, password: str) -> bool:
    return user.password == password


def get_dates_available_for_making_order() -> list[datetime.date]:
    """Даты, на которые можно заказать обед."""
    dates = get_dates_from_tomorrow_to_weekends() or get_next_week_work_days()
    if not dates:
        return []

    tomorrow = get_tomorrow_date()
    if tomorrow in dates and datetime.datetime.now().time() > DEADLINE_TIME:
        dates.remove(tomorrow)

    return dates


def get_dates_from_tomorrow_to_weekends() -> list[datetime.date]:
    """Даты начиная с завтрашней и до пятницы текущей недели включительно."""
    saturday_iso = 6
    tomorrow = get_tomorrow_date()
    from_tomorrow_to_weekend = saturday_iso - tomorrow.isoweekday()

    return [tomorrow + datetime.timedelta(days=index) for index in range(from_tomorrow_to_weekend)]


def get_next_week_work_days() -> list[datetime.date]:
    """Будни следующей недели."""
    today = datetime.date.today()
    tomorrow = get_tomorrow_date()

    next_monday = tomorrow + datetime.timedelta(days=7 - today.isoweekday())

    return [next_monday + datetime.timedelta(days=day_index) for day_index in range(5)]


def get_tomorrow_date() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=1)


def get_next_work_day() -> datetime.date:
    """Следующий рабочий день (завтра либо понедельник)"""
    today = datetime.date.today()
    today_iso = today.isoweekday()
    saturday_iso = 6
    if today_iso + 1 < saturday_iso:
        return today + datetime.timedelta(days=1)
    return today + datetime.timedelta(days=7 - today_iso)


async def get_dish_mode(db_session: AsyncSession, dish: entities.Dish) -> str:
    if dish in await DishManager(session=db_session).get_standard_second_dishes():
        return DishMode.STANDARD

    return DishMode.CONSTRUCTOR
