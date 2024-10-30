from typing import Any

import utils
from database import queries
from litestar import Request, get, post
from litestar.exceptions import NotAuthorizedException
from litestar.response import Redirect, Template


@get(path='/empty')
async def empty() -> str:
    return ''


@get(path='/')
async def index(request: 'Request[Any, Any, Any]') -> Template:
    return Template(template_name='index.html')


@get(path='/login_page')
async def login_page() -> Template:
    return Template(template_name='login_page.html')


@post(path='/login')
async def login(request: 'Request[Any, Any, Any]') -> Redirect:
    form = await request.form()
    user = queries.get_user_by_username(username=form['username'])

    if not user or not utils.check_password(user=user, password=form['password']):
        raise NotAuthorizedException

    request.set_session({'user_id': user.id})

    return Redirect('/')


@post(path='/logout')
async def logout(request: 'Request[Any, Any, Any]') -> Redirect:
    request.clear_session()

    return Redirect('/login_page')
