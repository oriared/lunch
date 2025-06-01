from typing import TYPE_CHECKING, Any

from web.dtos import RequestUserDTO

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection


async def retrieve_user_handler(
    session: dict[str, Any],
    connection: 'ASGIConnection[Any, Any, Any, Any]',  # noqa: ARG001
) -> RequestUserDTO | None:
    return RequestUserDTO(**session['user']) if 'user' in session else None
