from typing import Any

from litestar.connection import ASGIConnection

import dto
from database import models, queries


async def retrieve_user_handler(
    session: dict[str, Any], connection: 'ASGIConnection[Any, Any, Any, Any]'
) -> dto.User | None:
    return queries.get_user_by_id(user_id=user_id) if (user_id := session.get('user_id')) else None


def check_password(user: 'models.User', password: str) -> bool:
    return user.password == password
