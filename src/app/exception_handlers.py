from api import exception_handlers as api_exception_handlers
from litestar import Response
from litestar.connection import Request
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.response import Redirect, Template
from web import exception_handlers as web_exception_handlers


def authentication_error_handler(request: Request, exc: NotAuthorizedException) -> Redirect | Response:
    if request.url.path.startswith('/api/'):
        handler = api_exception_handlers.authentication_error_handler
    else:
        handler = web_exception_handlers.authentication_error_handler
    return handler(request, exc)


def page_not_found_error_handler(request: Request, exc: NotFoundException) -> Template | Response:
    if request.url.path.startswith('/api/'):
        handler = api_exception_handlers.page_not_found_error_handler
    else:
        handler = web_exception_handlers.page_not_found_error_handler
    return handler(request, exc)
