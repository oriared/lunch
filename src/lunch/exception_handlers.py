from litestar.connection import Request
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.response import Redirect, Template


def authentication_error_handler(_: Request, exc: NotAuthorizedException) -> Redirect:  # noqa: ARG001
    return Redirect('/login_page')


def page_not_found_error_handler(_: Request, exc: NotFoundException) -> Template:  # noqa: ARG001
    return Template(template_name='404.html')
