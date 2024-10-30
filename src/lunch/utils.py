import datetime
from typing import Any

from litestar.connection import ASGIConnection

import dto
from database import models, queries


async def retrieve_user_handler(
    session: dict[str, Any], connection: 'ASGIConnection[Any, Any, Any, Any]'
) -> dto.User | None:
    return queries.get_user_by_id(user_id=user_id) if (user_id := session.get('user_id')) else None


def check_password(user: 'models.User', password: str) -> bool:
    return user.password == password


def get_order_date_choices() -> list[datetime.date]:
    """
    :return: список дат, на которые можно заказать обед
    """
    return get_dates_from_tomorrow_to_weekends() or get_next_week_work_days()


def get_dates_from_tomorrow_to_weekends() -> list[datetime.date]:
    """
    :return: список дат начиная с завтрашней и до пятницы текущей недели включительно
    """
    saturday_iso = 6
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    dates = [tomorrow + datetime.timedelta(days=x) for x in range(saturday_iso - tomorrow.isoweekday())]

    return dates


def get_next_week_work_days() -> list[datetime.date]:
    """
    :return: список дат будней следующей недели
    """
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    next_monday = tomorrow + datetime.timedelta(days=7 - today.isoweekday())

    dates = [next_monday + datetime.timedelta(days=x) for x in range(5)]

    return dates
