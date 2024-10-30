import datetime

from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar import get, post

import consts
import dto
import utils
from database import queries


@get(path='/users')
async def users() -> HTMXTemplate:
    context = {'users': queries.get_users()}
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/my-orders')
async def my_orders(request: HTMXRequest) -> HTMXTemplate:
    context = {'orders': queries.get_user_orders(user=request.user)}
    return HTMXTemplate(template_name='my-orders.html', context=context, push_url=False)


@get(path='/order-form')
async def order_form() -> HTMXTemplate:
    context = {
        'date_choices': utils.get_order_date_choices(),
        'dishes': queries.first_dishes(),
        'second_dishes': queries.get_standard_second_dishes(),
    }
    return HTMXTemplate(template_name='order-form.html', context=context, push_url=False)


@get(path='/first-dishes')
async def first_dishes(vegan: str | None = None) -> HTMXTemplate:
    dishes = queries.get_vegan_dishes() if vegan else queries.first_dishes()
    return HTMXTemplate(template_name='first-dishes.html', context={'dishes': dishes}, push_url=False)


@get(path='/second-dishes')
async def second_dishes(dish_mode: str) -> HTMXTemplate:
    context = {'mode': dish_mode}
    if dish_mode == consts.DishMode.STANDARD:
        context['second_dishes'] = queries.get_standard_second_dishes()
    elif dish_mode == consts.DishMode.CONSTRUCTOR:
        context['second_dishes_first_part'] = queries.get_constructor_second_dishes(part='first')
        context['second_dishes_second_part'] = queries.get_constructor_second_dishes(part='second')
    return HTMXTemplate(template_name='second-dishes.html', context=context, push_url=False)


@post(path='/save-order')
async def save_order(request: HTMXRequest) -> HTMXTemplate:
    form = await request.form()

    order_date = datetime.date.fromisoformat(form['order_date'])
    lunch = dto.Lunch(
        date=order_date,
        dish_mode=form['dish_mode'],
        first_dish=form['first_dish'],
        second_dish_first_part=form['second_dish_first_part'],
        second_dish_second_part=form.get('second_dish_second_part', ''),
        comment=form.get('comment', ''),
    )

    queries.save_order(lunch=lunch, user=request.user)
    return HTMXTemplate(template_name='save-order.html', push_url=False)
