import datetime

import consts
import dto
import utils
from database import queries
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.response import Redirect


@get(path='/users')
async def users() -> HTMXTemplate:
    context = {'users': queries.get_users()}
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/my-orders')
async def my_orders(request: HTMXRequest) -> HTMXTemplate:
    context = {'orders': queries.get_user_orders(user=request.user)}
    return HTMXTemplate(template_name='my-orders.html', context=context, push_url=False)


@get(path='/order-form')
async def order_form(
    request: HTMXRequest,
    order_date: datetime.date | None = None,
) -> HTMXTemplate:
    date_choices = utils.get_order_date_choices()
    selected_date = order_date
    if not selected_date and date_choices:
        selected_date = date_choices[0]

    context = {
        'date_choices': date_choices,
        'dishes': queries.get_first_dishes(),
        'second_dishes': queries.get_standard_second_dishes(),
        'second_dishes_first_part': queries.get_constructor_second_dishes(part='first'),
        'second_dishes_second_part': queries.get_constructor_second_dishes(part='second'),
        'selected_date': selected_date,
        'selected_dish_mode': consts.DishMode.STANDARD,
    }

    if selected_date:
        user_orders = queries.get_orders_by_date(date=selected_date, orders=queries.get_user_orders(user=request.user))
        if user_orders:
            order = user_orders[0]
            selected_second_dish_first_part = queries.get_order_second_dish_first_part(order)
            selected_second_dish_second_part = queries.get_order_second_dish_second_part(order)

            if selected_second_dish_first_part:
                dish_mode = utils.get_dish_mode(selected_second_dish_first_part)
            elif selected_second_dish_second_part:
                dish_mode = utils.get_dish_mode(selected_second_dish_second_part)
            else:
                dish_mode = consts.DishMode.STANDARD

            context.update(
                {
                    'selected_first_dish': queries.get_order_first_dish(order),
                    'selected_second_dish': queries.get_order_second_dish(order),
                    'selected_second_dish_first_part': selected_second_dish_first_part,
                    'selected_second_dish_second_part': selected_second_dish_second_part,
                    'selected_dish_mode': dish_mode,
                    'comment': order.comment,
                }
            )

    return HTMXTemplate(template_name='order-form.html', context=context, push_url=False)


@get(path='/first-dishes')
async def first_dishes(vegan: bool | None = None) -> HTMXTemplate:
    dishes = queries.get_vegan_dishes() if vegan else queries.get_first_dishes()
    return HTMXTemplate(template_name='first-dishes.html', context={'dishes': dishes}, push_url=False)


@get(path='/second-dishes')
async def second_dishes(dish_mode: str) -> HTMXTemplate:
    context = {'selected_dish_mode': dish_mode}
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


@post(path='/cancel-order')
async def cancel_order(request: HTMXRequest, order_date: datetime.date) -> Redirect:
    order = queries.get_order(date=order_date, user=request.user)
    queries.delete_order(order=order)

    return Redirect('/my-orders')
