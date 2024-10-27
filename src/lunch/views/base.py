from dataclasses import dataclass
from typing import Any

from litestar import get, Request, post
from litestar.exceptions import NotAuthorizedException
from litestar.response import Redirect, Template

import utils
from database import queries


@get(path='/')
async def index(request: 'Request[Any, Any, Any]') -> Template:
    context = {'user': request.user}
    return Template(template_name='index.html', context=context)


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
