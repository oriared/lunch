from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core import entities
from core.interactors import UserManager
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection


@dataclass
class RequestUserDTO:
    id: int
    username: str
    name: str
    is_admin: bool


async def provide_transaction(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


async def retrieve_user_handler(
    session: dict[str, Any],
    connection: 'ASGIConnection[Any, Any, Any, Any]',  # noqa: ARG001
) -> RequestUserDTO | None:
    return RequestUserDTO(**session['user']) if 'user' in session else None


async def validate_user_data(
    db_session: AsyncSession, data: dict[str, Any], user: entities.User | None = None
) -> tuple[bool, dict[str, str]]:
    errors = {}
    required_fields = ['username', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            errors[field] = 'Обязательное поле'

    if data.get('username'):
        user_with_same_username = await UserManager(session=db_session).get_by_username(username=data['username'])
        if user_with_same_username and user_with_same_username.id != user.id:
            errors['username'] = 'Такой пользователь уже существует'

    if data.get('password') and len(data['password']) < 4:
        errors['password'] = 'Минимальная длина пароля 4 символа'  # noqa: S105

    if data.get('name') and len(data['name']) < 3:
        errors['name'] = 'Минимальная длина имени 3 символа'

    return bool(not errors), errors
