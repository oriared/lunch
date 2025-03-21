import csv
import datetime
import io

from core import entities
from core.interactors import DishManager, OrderManager, UserManager


def get_selected_date_for_order_form(
    user: entities.User,
    order: entities.Order | None,
    order_date: datetime.date | None,
    date_choices: list[datetime.date],
) -> datetime.date | None:
    if order:
        selected_date = order.date
    elif order_date:
        selected_date = order_date
    elif date_choices and user:
        for date in date_choices:
            if not OrderManager().get_by_user_id_and_date(user_id=user.id, date=date):
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
    orders = OrderManager().get_by_date(date=date)

    headers = ['ФИО', 'Заказ', 'Комментарий']
    rows = []
    for order in orders:
        user = UserManager().get_by_id(order.user_id)
        dishes = DishManager().get_by_order_id(order_id=order.id)
        dishes_text = ', '.join([dish.name for dish in dishes])
        rows.append([user.name if user else '-', dishes_text, order.comment or ''])

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
