import locale
from pathlib import Path

from config import DatabaseConfig
from core.database.di import provide_db_session
from exception_handlers import authentication_error_handler, page_not_found_error_handler
from litestar import Litestar
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.middleware.session.server_side import ServerSideSessionBackend, ServerSideSessionConfig
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from litestar.security.session_auth import SessionAuth
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from web.auth import retrieve_user_handler
from web.dtos import RequestUserDTO
from web.views import admin_htmx_blocks, base, orders_htmx_blocks

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))

static_files_handler = create_static_files_router(path='/static', directories=[Path('web/static')], name='static')

route_handlers = [
    base.login_page,
    base.login,
    base.logout,
    base.index,
    admin_htmx_blocks.users_list,
    admin_htmx_blocks.user_form,
    admin_htmx_blocks.save_user,
    admin_htmx_blocks.orders_list,
    admin_htmx_blocks.cancel_order,
    admin_htmx_blocks.download_orders_report,
    orders_htmx_blocks.my_orders,
    orders_htmx_blocks.order_form,
    orders_htmx_blocks.first_dishes,
    orders_htmx_blocks.second_dishes,
    orders_htmx_blocks.save_order,
    orders_htmx_blocks.cancel_order,
    static_files_handler,
]

template_config = TemplateConfig(directory=Path('web/templates'), engine=JinjaTemplateEngine)

session_auth = SessionAuth[RequestUserDTO, ServerSideSessionBackend](
    retrieve_user_handler=retrieve_user_handler,
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
    dependencies={'db_session': provide_db_session},
    plugins=[SQLAlchemyPlugin(DatabaseConfig.config)],
)
