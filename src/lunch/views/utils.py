import csv
import datetime
import io

import dto
from database import models, queries


def get_selected_date_for_order_form(
    user: dto.User,
    order: models.Order | None,
    order_date: datetime.date | None,
    date_choices: list[datetime.date],
    anonymous: bool,
) -> datetime.date | None:
    if order:
        selected_date = order.date
    elif order_date:
        selected_date = order_date
    elif date_choices and not anonymous:
        for date in date_choices:
            if not queries.get_user_order_by_date(user=user, date=date):
                selected_date = date
                break
        else:
            selected_date = date_choices[0]
    elif date_choices:
        selected_date = date_choices[0]
    else:
        selected_date = None
    return selected_date


def get_orders_report_bytes(date: datetime.date) -> bytes:
    orders = queries.get_orders_by_date(date=date)

    headers = ['ФИО', 'Заказ', 'Комментарий']
    rows = [[order.user_id or '-', order.dishes_text, order.comment or ''] for order in orders]

    return generate_csv_bytes(rows=rows, headers=headers)


def generate_csv_bytes(rows: list[list[str | int | float]], headers: list[str] | None = None) -> bytes:
    """
    Генерирует CSV-файл и возвращает его содержимое в виде байтов.

    :param rows: Список списков с данными (строки CSV).
    :param headers: Список заголовков (опционально).
    :return: CSV-файл в виде байтов.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    if headers:
        writer.writerow(headers)

    writer.writerows(rows)

    return output.getvalue().encode('utf-8')
