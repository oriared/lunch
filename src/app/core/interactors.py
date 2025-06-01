import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core import entities
from core.repositories import UserRepo
from core.services.user import UserCreateOrUpdateDTO, UserValidator


class UserInteractor:
    @classmethod
    async def save_user(cls, user: entities.User | None, user_data: dict, db_session: AsyncSession) -> entities.User:
        user_dto = UserCreateOrUpdateDTO()

        if user:
            user_dto.id = user.id
            user_dto.username = user.username
            user_dto.password = user.password
            user_dto.name = user.name
            user_dto.is_admin = user.is_admin
            user_dto.is_active = user.is_active
            user_dto.joined_dt = user.joined_dt

        for field, value in user_data.items():
            setattr(user_dto, field, value)

        await UserValidator.validate_user_data(user_data=user_dto, db_session=db_session)

        if not user_dto.id:
            user_dto.joined_dt = datetime.datetime.now()

        return await UserRepo(session=db_session, user=user).save(user_data=user_dto)
