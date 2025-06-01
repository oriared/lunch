import datetime
from math import ceil

from core.interactors import UserInteractor
from core.repositories import DishRepo, OrderRepo, UserRepo
from core.services import calendar
from core.services.user import ValidationError
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.response import Redirect, Response
from sqlalchemy.ext.asyncio import AsyncSession

from web import consts
from web.views.utils import get_orders_report_bytes


@get(path='/admin/users')
async def users_list(db_session: AsyncSession, page: int = 1) -> HTMXTemplate:
    users_count = await UserRepo(session=db_session).get_count()
    page_users = await UserRepo(session=db_session).get_all(page=page, per_page=consts.USERS_PER_PAGE)
    context = {
        'users': page_users,
        'selected_module': 'users',
        'page': page,
        'pages_count': ceil(users_count / consts.USERS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='admin-panel.html', context=context, push_url=False)


@get(path='/admin/orders')
async def orders_list(db_session: AsyncSession, page: int = 1) -> HTMXTemplate:
    orders_count = await OrderRepo(session=db_session).get_count()
    orders = await OrderRepo(session=db_session).get_all(page=page, per_page=consts.ORDERS_PER_PAGE)
    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': ', '.join(
                dish.name for dish in await DishRepo(session=db_session).get_by_order_id(order.id)
            ).capitalize(),
            'user': await UserRepo(session=db_session).get_by_id(order.user_id),
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
async def save_user(request: HTMXRequest, db_session: AsyncSession, user_id: int | None = None) -> HTMXTemplate:
    user = await UserRepo(session=db_session).get_by_id(user_id=user_id) if user_id else None

    form = await request.form()

    user_data = {}

    for k, v in form.items():
        if k in ('is_admin', 'is_active'):
            user_data[k] = v == 'on'
        else:
            user_data[k] = v

    try:
        await UserInteractor.save_user(user=user, user_data=user_data, db_session=db_session)
    except ValidationError as e:
        context = {'user': user, 'errors': e.detail}
        return HTMXTemplate(template_name='user-form.html', context=context, push_url=False)

    users_count = await UserRepo(session=db_session).get_count()
    context = {
        'users': await UserRepo(session=db_session).get_all(page=1, per_page=consts.USERS_PER_PAGE),
        'page': 1,
        'pages_count': ceil(users_count / consts.USERS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/admin/user-form')
async def user_form(db_session: AsyncSession, user_id: int | None = None) -> HTMXTemplate:
    user = await UserRepo(session=db_session).get_by_id(user_id=user_id)
    context = {'user': user}
    return HTMXTemplate(template_name='user-form.html', context=context, push_url=False)


@post(path='/admin/cancel-order')
async def cancel_order(db_session: AsyncSession, order_id: int) -> Redirect:
    order = await OrderRepo(session=db_session).get_by_id(order_id=order_id)
    await OrderRepo(session=db_session, order=order).delete()
    await db_session.commit()

    return Redirect('/admin/orders')


@get(path='/admin/download-orders-report')
async def download_orders_report(db_session: AsyncSession) -> Response:
    report_bytes = await get_orders_report_bytes(db_session=db_session, date=calendar.get_next_work_day())
    return Response(
        media_type='text/csv',
        content=report_bytes,
        headers={'Content-Disposition': 'attachment; filename="order.csv"'},
    )
