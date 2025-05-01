from typing import TYPE_CHECKING, Any

from core import entities
from core.interactors import UserManager

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection


async def retrieve_user_handler(
    session: dict[str, Any],
    connection: 'ASGIConnection[Any, Any, Any, Any]',  # noqa: ARG001
) -> entities.User | None:
    user_id = session.get('user_id')
    return UserManager().get_by_id(user_id=user_id) if user_id else None


def validate_user_data(data: dict[str, Any], user: entities.User | None = None) -> tuple[bool, dict[str, str]]:
    errors = {}
    required_fields = ['username', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            errors[field] = 'Обязательное поле'

    if data.get('username'):
        user_with_same_username = UserManager().get_by_username(username=data['username'])
        if user_with_same_username and user_with_same_username.id != user.id:
            errors['username'] = 'Такой пользователь уже существует'

    if data.get('password') and len(data['password']) < 4:
        errors['password'] = 'Минимальная длина пароля 4 символа'  # noqa: S105

    if data.get('name') and len(data['name']) < 3:
        errors['name'] = 'Минимальная длина имени 3 символа'

    return bool(not errors), errors
