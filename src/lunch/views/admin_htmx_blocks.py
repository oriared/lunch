import datetime
from math import ceil

import consts
from common_utils import validate_user_data
from core import datatools, entities
from core.interactors import DishManager, OrderManager, UserManager
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.response import Redirect, Response

from views.utils import get_orders_report_bytes


@get(path='/admin/users')
async def users_list(page: int = 1) -> HTMXTemplate:
    users_count = UserManager().get_count()
    page_users = UserManager().get_all(page=page, per_page=consts.USERS_PER_PAGE)
    context = {
        'users': page_users,
        'selected_module': 'users',
        'page': page,
        'pages_count': ceil(users_count / consts.USERS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='admin-panel.html', context=context, push_url=False)


@get(path='/admin/orders')
async def orders_list(page: int = 1) -> HTMXTemplate:
    orders_count = OrderManager().get_count()
    orders = OrderManager().get_all(page=page, per_page=consts.ORDERS_PER_PAGE)
    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': DishManager().get_by_order_id(order.id),
            'user': UserManager().get_by_id(order.user_id),
        }
        for order in orders
    ]
    context = {
        'today': datetime.date.today(),
        'orders': page_orders,
        'selected_module': 'orders',
        'page': page,
        'pages_count': ceil(orders_count / consts.USERS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='admin-panel.html', context=context, push_url=False)


@post(path='/admin/save-user')
async def save_user(request: HTMXRequest, user_id: int | None = None) -> HTMXTemplate:
    user = UserManager().get_by_id(user_id=user_id) if user_id else None

    form = await request.form()

    user_data = {
        'username': form.get('username', ''),
        'password': form.get('password', ''),
        'name': form.get('name', ''),
        'is_admin': form.get('is_admin', False),
    }

    is_valid, errors = validate_user_data(data=user_data, user=user)

    if not is_valid:
        context = {'user': user, 'errors': errors}
        return HTMXTemplate(template_name='user-form.html', context=context, push_url=False)

    if user:
        user.username = user_data['username']
        user.password = user_data['password']
        user.name = user_data['name']
        user.is_admin = user_data['is_admin']
    else:
        user = entities.User(
            id=None,
            username=user_data['username'],
            password=user_data['password'],
            name=user_data['name'],
            joined_dt=datetime.datetime.now(),
            is_admin=user_data['is_admin'],
        )

    UserManager(user).save()

    users_count = UserManager().get_count()
    context = {
        'users': UserManager().get_all(page=1, per_page=consts.USERS_PER_PAGE),
        'page': 1,
        'pages_count': ceil(users_count / consts.USERS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/admin/user-form')
async def user_form(user_id: int | None = None) -> HTMXTemplate:
    user = UserManager().get_by_id(user_id=user_id)
    context = {'user': user}
    return HTMXTemplate(template_name='user-form.html', context=context, push_url=False)


@post(path='/admin/cancel-order')
async def cancel_order(order_id: int) -> Redirect:
    order = OrderManager().get_by_id(order_id=order_id)
    OrderManager(order).delete()

    return Redirect('/admin/orders')


@get(path='/admin/download-orders-report')
async def download_orders_report() -> Response:
    report_bytes = get_orders_report_bytes(datatools.get_next_work_day())
    return Response(
        media_type='text/csv',
        content=report_bytes,
        headers={'Content-Disposition': 'attachment; filename="order.csv"'},
    )
