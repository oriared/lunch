from database import queries
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from utils import validate_user_data


@get(path='/users')
async def users() -> HTMXTemplate:
    context = {'users': queries.get_users(), 'selected_module': 'users'}
    return HTMXTemplate(template_name='admin-panel.html', context=context, push_url=False)


@post(path='/save-user')
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

    context = {'users': queries.get_users()}
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/user-form')
async def user_form(user_id: int | None = None) -> HTMXTemplate:
    user = queries.get_user_by_id(user_id=user_id)
    context = {'user': user}
    return HTMXTemplate(template_name='user-form.html', context=context, push_url=False)
