import datetime
from math import ceil
from typing import Any

import common_utils
import consts
from database import queries
from litestar import Request, get, post
from litestar.exceptions import NotAuthorizedException
from litestar.response import Redirect, Template


@get(path='/')
async def index(request: Request) -> Template:
    orders = queries.get_user_orders(user=request.user)
    page_orders = queries.get_user_orders(user=request.user, page=1)
    context = {
        'orders': page_orders,
        'today': datetime.date.today(),
        'page': 1,
        'pages_count': ceil(len(orders) // consts.ITEMS_PER_PAGE) or 1,
    }
    return Template(template_name='index.html', context=context)


@get(path='/login_page')
async def login_page() -> Template:
    return Template(template_name='login_page.html')


@post(path='/login')
async def login(request: 'Request[Any, Any, Any]') -> Redirect:
    form = await request.form()
    user = queries.get_user_by_username(username=form['username'])

    if not user or not common_utils.check_password(user=user, password=form['password']):
        raise NotAuthorizedException

    request.set_session({'user_id': user.id})

    return Redirect('/')


@post(path='/logout')
async def logout(request: 'Request[Any, Any, Any]') -> Redirect:
    request.clear_session()

    return Redirect('/login_page')
