from litestar.response import Redirect
from litestar.exceptions import NotAuthorizedException


def authentication_error_handler(_, exc: NotAuthorizedException) -> Redirect:
    return Redirect('/login_page')
