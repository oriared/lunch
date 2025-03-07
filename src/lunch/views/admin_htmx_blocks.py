import datetime
from math import ceil

import consts
from database import queries
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.response import Redirect
from utils import validate_user_data


@get(path='/admin/users')
async def users_list(page: int = 1) -> HTMXTemplate:
    users = queries.get_users()
    page_users = queries.get_users(page=page)
    context = {
        'users': page_users,
        'selected_module': 'users',
        'page': page,
        'pages_count': ceil(len(users) / consts.ITEMS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='admin-panel.html', context=context, push_url=False)


@get(path='/admin/orders')
async def orders_list(page: int = 1) -> HTMXTemplate:
    orders = queries.get_orders()
    page_orders = queries.get_orders(page=page)
    context = {
        'today': datetime.date.today(),
        'orders': page_orders,
        'selected_module': 'orders',
        'page': page,
        'pages_count': ceil(len(orders) / consts.ITEMS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='admin-panel.html', context=context, push_url=False)


@post(path='/admin/save-user')
async def save_user(request: HTMXRequest, user_id: int | None = None) -> HTMXTemplate:
    user = queries.get_user_by_id(user_id=user_id)
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
        queries.update_user(user=user, user_data=user_data)
    else:
        queries.create_user(user_data=user_data)

    users = queries.get_users()
    context = {
        'users': queries.get_users(),
        'page': 1,
        'pages_count': ceil(len(users) / consts.ITEMS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/admin/user-form')
async def user_form(user_id: int | None = None) -> HTMXTemplate:
    user = queries.get_user_by_id(user_id=user_id)
    context = {'user': user}
    return HTMXTemplate(template_name='user-form.html', context=context, push_url=False)


@post(path='/admin/cancel-order')
async def cancel_order(order_id: int) -> Redirect:
    order = queries.get_order(order_id=order_id)
    queries.delete_order(order=order)

    return Redirect('/admin/orders')
