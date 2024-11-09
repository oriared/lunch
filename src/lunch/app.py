import locale
from pathlib import Path

import utils
from dto import User
from exception_handlers import authentication_error_handler, page_not_found_error_handler
from litestar import Litestar
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.middleware.session.server_side import ServerSideSessionBackend, ServerSideSessionConfig
from litestar.security.session_auth import SessionAuth
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from views import base, htmx_blocks

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))

static_files_handler = create_static_files_router(path='/static', directories=[Path('static')], name='static')

route_handlers = [
    base.login_page,
    base.login,
    base.logout,
    base.index,
    base.empty,
    htmx_blocks.users,
    htmx_blocks.my_orders,
    htmx_blocks.order_form,
    htmx_blocks.first_dishes,
    htmx_blocks.second_dishes,
    htmx_blocks.save_order,
    htmx_blocks.cancel_order,
    static_files_handler,
]

template_config = TemplateConfig(directory=Path('templates'), engine=JinjaTemplateEngine)

session_auth = SessionAuth[User, ServerSideSessionBackend](
    retrieve_user_handler=utils.retrieve_user_handler,
    session_backend_config=ServerSideSessionConfig(),
    exclude=['/login', '/schema', '/static/styles.css', '/static/favicon.ico'],
)

exception_handlers = {
    NotAuthorizedException: authentication_error_handler,
    NotFoundException: page_not_found_error_handler,
}


app = Litestar(
    route_handlers=route_handlers,
    request_class=HTMXRequest,
    template_config=template_config,
    on_app_init=[session_auth.on_app_init],
    exception_handlers=exception_handlers,
)
