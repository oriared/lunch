from sqlalchemy.ext.asyncio import AsyncSession

from core import entities
from core.dtos import UserCreateOrUpdateDTO
from core.exceptions import ValidationError
from core.repositories import UserRepo


class UserValidator:
    required_fields = ('username', 'password', 'name')

    @classmethod
    async def validate_user_data(cls, user_data: UserCreateOrUpdateDTO, db_session: AsyncSession) -> None:
        errors = {}

        for field in cls.required_fields:
            if not getattr(user_data, field):
                errors[field] = 'Обязательное поле'

        user_with_same_username = await UserRepo(session=db_session).get_by_username(username=user_data.username)
        if user_with_same_username and (not user_data.id or user_with_same_username.id != user_data.id):
            errors['username'] = 'Такой пользователь уже существует'

        if len(user_data.password) < 4:
            errors['password'] = 'Минимальная длина пароля 4 символа'  # noqa: S105

        if len(user_data.name) < 3:
            errors['name'] = 'Минимальная длина имени 3 символа'

        if errors:
            raise ValidationError(detail=errors)


class PasswordChecker:
    @classmethod
    def check(cls, user: entities.User, password: str) -> bool:
        return user.password == password
