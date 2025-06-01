from sqlalchemy.ext.asyncio import AsyncSession

from core import entities
from core.consts import DishMode
from core.repositories import DishRepo


async def get_dish_mode(db_session: AsyncSession, dish: entities.Dish) -> str:
    if dish in await DishRepo(session=db_session).get_standard_second_dishes():
        return DishMode.STANDARD

    return DishMode.CONSTRUCTOR
