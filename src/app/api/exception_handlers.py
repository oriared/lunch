from litestar import Response
from litestar.connection import Request
from litestar.exceptions import NotAuthorizedException, NotFoundException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND


def authentication_error_handler(_: Request, exc: NotAuthorizedException) -> Response:  # noqa: ARG001
    return Response({'error': 'Вы не авторизованы'}, status_code=HTTP_401_UNAUTHORIZED)


def page_not_found_error_handler(_: Request, exc: NotFoundException) -> Response:  # noqa: ARG001
    return Response({'error': 'Страница не найдена'}, status_code=HTTP_404_NOT_FOUND)
