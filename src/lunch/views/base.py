import datetime
from dataclasses import asdict
from math import ceil

import consts
from common_utils import RequestUserDTO
from core import datatools
from core.interactors import DishManager, OrderManager, UserManager
from litestar import Request, get, post
from litestar.exceptions import NotAuthorizedException
from litestar.response import Redirect, Template
from sqlalchemy.ext.asyncio import AsyncSession


@get(path='/')
async def index(request: Request, db_session: AsyncSession) -> Template:
    user_orders_count = await OrderManager(session=db_session).get_user_orders_count(user_id=request.user.id)
    orders = await OrderManager(session=db_session).get_by_user_id(
        user_id=request.user.id, page=1, per_page=consts.ORDERS_PER_PAGE
    )
    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': ', '.join(
                dish.name for dish in await DishManager(session=db_session).get_by_order_id(order.id)
            ).capitalize(),
        }
        for order in orders
    ]
    context = {
        'orders': page_orders,
        'today': datetime.date.today(),
        'page': 1,
        'pages_count': ceil(user_orders_count // consts.ORDERS_PER_PAGE) or 1,
    }
    return Template(template_name='index.html', context=context)


@get(path='/login_page')
async def login_page() -> Template:
    return Template(template_name='login_page.html')


@post(path='/login')
async def login(request: Request, db_session: AsyncSession) -> Redirect:
    form = await request.form()
    user = await UserManager(session=db_session).get_by_username(username=form['username'])

    if not user or not datatools.check_password(user=user, password=form['password']):
        raise NotAuthorizedException

    user_dto = RequestUserDTO(id=user.id, username=user.username, name=user.name, is_admin=user.is_admin)
    request.set_session({'user': asdict(user_dto)})

    return Redirect('/')


@post(path='/logout')
async def logout(request: Request) -> Redirect:
    request.clear_session()

    return Redirect('/login_page')
