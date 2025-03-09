import datetime
from math import ceil

import consts
import dto
import utils
from database import queries
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.exceptions import NotFoundException
from litestar.response import Redirect


@get(path='/my-orders')
async def my_orders(request: HTMXRequest, page: int = 1) -> HTMXTemplate:
    orders = queries.get_user_orders(user=request.user)
    page_orders = queries.get_user_orders(user=request.user, page=page)
    context = {
        'orders': page_orders,
        'today': datetime.date.today(),
        'selected_module': 'my-orders',
        'page': page,
        'pages_count': ceil(len(orders) / consts.ITEMS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='lunch-block.html', context=context, push_url=False)


@get(path='/order-form')
async def order_form(
    request: HTMXRequest,
    order_id: int | None = None,
    order_date: datetime.date | None = None,
    is_admin: bool = False,
    anonymous: bool = False,
) -> HTMXTemplate:
    date_choices = utils.get_order_date_choices()
    order = queries.get_order(order_id=order_id) if order_id else None

    if order:
        selected_date = order.date
    elif order_date:
        selected_date = order_date
    elif date_choices:
        selected_date = date_choices[0]
    else:
        selected_date = None

    if not selected_date:
        raise NotFoundException

    if not order and not anonymous:
        user_orders = queries.get_orders_by_date(date=selected_date, orders=queries.get_user_orders(user=request.user))
        if user_orders:
            order = user_orders[0]

    context = {
        'selected_module': 'order-form',
        'date_choices': date_choices,
        'dishes': queries.get_first_dishes(date=selected_date),
        'second_dishes': queries.get_standard_second_dishes(date=selected_date),
        'second_dishes_first_part': queries.get_constructor_second_dishes(part='first', date=selected_date),
        'second_dishes_second_part': queries.get_constructor_second_dishes(part='second', date=selected_date),
        'selected_date': selected_date,
        'selected_dish_mode': consts.DishMode.STANDARD,
        'is_admin': is_admin,
        'anonymous': anonymous,
    }

    if order:
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
                'order': order,
                'selected_first_dish': queries.get_order_first_dish(order),
                'selected_second_dish': queries.get_order_second_dish(order),
                'selected_second_dish_first_part': selected_second_dish_first_part,
                'selected_second_dish_second_part': selected_second_dish_second_part,
                'selected_dish_mode': dish_mode,
                'comment': order.comment,
            }
        )

    return HTMXTemplate(template_name='lunch-block.html', context=context, push_url=False)


@get(path='/first-dishes')
async def first_dishes(date: datetime.date, vegan: bool | None = None) -> HTMXTemplate:
    dishes = queries.get_vegan_dishes(date=date) if vegan else queries.get_first_dishes(date=date)
    return HTMXTemplate(template_name='first-dishes.html', context={'dishes': dishes}, push_url=False)


@get(path='/second-dishes')
async def second_dishes(date: datetime.date, dish_mode: str) -> HTMXTemplate:
    context = {'selected_dish_mode': dish_mode}
    if dish_mode == consts.DishMode.STANDARD:
        context['second_dishes'] = queries.get_standard_second_dishes(date=date)
    elif dish_mode == consts.DishMode.CONSTRUCTOR:
        context['second_dishes_first_part'] = queries.get_constructor_second_dishes(part='first', date=date)
        context['second_dishes_second_part'] = queries.get_constructor_second_dishes(part='second', date=date)
    return HTMXTemplate(template_name='second-dishes.html', context=context, push_url=False)


@post(path='/save-order')
async def save_order(
    request: HTMXRequest, order_id: int | None = None, is_admin: bool = False, anonymous: bool = False, page: int = 1
) -> HTMXTemplate:
    form = await request.form()

    context = {
        'today': datetime.date.today(),
        'selected_module': 'my-orders',
    }

    if any([form['first_dish'], form['second_dish_first_part'], form.get('second_dish_second_part')]):
        order_date = datetime.date.fromisoformat(form['order_date'])
        lunch = dto.Lunch(
            date=order_date,
            dish_mode=form['dish_mode'],
            first_dish=form['first_dish'],
            second_dish_first_part=form['second_dish_first_part'],
            second_dish_second_part=form.get('second_dish_second_part', ''),
            comment=form.get('comment', ''),
        )
        if order_id:
            order = queries.get_order(order_id=order_id)
            queries.update_order(order=order, lunch=lunch)
        else:
            user = request.user if not anonymous else None
            order = queries.create_order(lunch=lunch, user=user)
        context['updated_order'] = order
    elif order_id:
        queries.delete_order(order=queries.get_order(order_id=order_id))

    if is_admin:
        orders = queries.get_orders()
        page_orders = queries.get_orders(page=1)
    else:
        orders = queries.get_user_orders(user=request.user)
        page_orders = queries.get_user_orders(user=request.user, page=1)

    context.update(
        {
            'orders': page_orders,
            'page': page,
            'pages_count': ceil(len(orders) / consts.ITEMS_PER_PAGE) or 1,
        }
    )

    template_name = 'orders.html' if is_admin else 'lunch-block.html'

    return HTMXTemplate(template_name=template_name, context=context, push_url=False)


@post(path='/cancel-order')
async def cancel_order(order_id: int) -> Redirect:
    order = queries.get_order(order_id=order_id)
    queries.delete_order(order=order)

    return Redirect('/my-orders')
