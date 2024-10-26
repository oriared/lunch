from litestar.response import Redirect, Template
from litestar.exceptions import NotAuthorizedException, NotFoundException


def authentication_error_handler(_, exc: NotAuthorizedException) -> Redirect:
    return Redirect('/login_page')


def page_not_found_error_handler(_, exc: NotFoundException) -> Template:
    return Template(template_name='404.html')
