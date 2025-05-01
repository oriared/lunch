import datetime
from math import ceil

import consts
from core import datatools, entities
from core.consts import DEADLINE_TIME, DishMode
from core.interactors import DishManager, OrderManager, UserManager
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.exceptions import NotFoundException
from litestar.response import Redirect

from views.utils import get_selected_date_for_order_form


@get(path='/my-orders')
async def my_orders(request: HTMXRequest, page: int = 1) -> HTMXTemplate:
    orders_count = OrderManager().get_count(user_id=request.user.id)
    orders = OrderManager().get_by_user_id(user_id=request.user.id, page=page, per_page=consts.ORDERS_PER_PAGE)
    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': DishManager().get_by_order_id(order.id),
        }
        for order in orders
    ]
    context = {
        'orders': page_orders,
        'today': datetime.date.today(),
        'selected_module': 'my-orders',
        'page': page,
        'pages_count': ceil(orders_count / consts.ORDERS_PER_PAGE) or 1,
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
    date_choices = datatools.get_dates_available_for_making_order()
    order = OrderManager().get_by_id(order_id=order_id) if order_id else None

    selected_date = get_selected_date_for_order_form(
        user=request.user if not anonymous else None,
        order=order,
        order_date=order_date,
        date_choices=date_choices,
    )
    if not selected_date:
        raise NotFoundException('Нет доступных дат для заказа')

    if not order and not anonymous:
        user_orders = OrderManager().get_by_user_id_and_date(date=selected_date, user_id=request.user.id)
        if user_orders:
            order = user_orders[0]

    context = {
        'selected_module': 'order-form',
        'date_choices': date_choices,
        'dishes': DishManager().get_first_dishes(date=selected_date),
        'second_dishes': DishManager().get_standard_second_dishes(date=selected_date),
        'second_dishes_first_part': DishManager().get_constructor_second_dishes_first_part(date=selected_date),
        'second_dishes_second_part': DishManager().get_constructor_second_dishes_second_part(date=selected_date),
        'selected_date': selected_date,
        'selected_dish_mode': DishMode.STANDARD,
        'is_admin': is_admin,
        'anonymous': anonymous,
        'order_user': UserManager().get_by_id(user_id=request.user.id) if not anonymous else None,
    }

    if order:
        selected_second_dish_first_part = DishManager().get_order_second_dish_first_part(order_id=order.id)
        selected_second_dish_second_part = DishManager().get_order_second_dish_second_part(order_id=order.id)
        if selected_second_dish_first_part:
            dish_mode = datatools.get_dish_mode(selected_second_dish_first_part)
        elif selected_second_dish_second_part:
            dish_mode = DishMode.CONSTRUCTOR
        else:
            dish_mode = DishMode.STANDARD

        context.update(
            {
                'order': order,
                'selected_first_dish': DishManager().get_order_first_dish(order_id=order.id),
                'selected_second_dish': DishManager().get_order_second_dish(order_id=order.id),
                'selected_second_dish_first_part': selected_second_dish_first_part,
                'selected_second_dish_second_part': selected_second_dish_second_part,
                'selected_dish_mode': dish_mode,
                'comment': order.comment,
                'order_user': UserManager().get_by_id(user_id=order.user_id) if order.user_id else None,
            }
        )

    return HTMXTemplate(template_name='lunch-block.html', context=context, push_url=False)


@get(path='/first-dishes')
async def first_dishes(date: datetime.date, vegan: bool | None = None) -> HTMXTemplate:
    dishes = DishManager().get_vegan_dishes(date=date) if vegan else DishManager().get_first_dishes(date=date)
    return HTMXTemplate(template_name='first-dishes.html', context={'dishes': dishes}, push_url=False)


@get(path='/second-dishes')
async def second_dishes(date: datetime.date, dish_mode: str) -> HTMXTemplate:
    context = {'selected_dish_mode': dish_mode}
    if dish_mode == DishMode.STANDARD:
        context['second_dishes'] = DishManager().get_standard_second_dishes(date=date)
    elif dish_mode == DishMode.CONSTRUCTOR:
        context['second_dishes_first_part'] = DishManager().get_constructor_second_dishes_first_part(date=date)
        context['second_dishes_second_part'] = DishManager().get_constructor_second_dishes_second_part(date=date)
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

    order = OrderManager().get_by_id(order_id=order_id) if order_id else None
    order_date = datetime.date.fromisoformat(form['order_date'])

    if not request.user.is_admin and (order.date if order else order_date) <= datetime.date.today():
        return HTMXTemplate(
            template_str='Нельзя изменять уже завершенные заказы',
            push_url=False,
            re_target='#errorBlock',
            re_swap='innerHTML',
        )

    if (
        not request.user.is_admin
        and (order.date if order else order_date) == datetime.date.today() + datetime.timedelta(days=1)
        and datetime.datetime.now().time() > DEADLINE_TIME
    ):
        return HTMXTemplate(
            template_str=f'Заказ на завтра нельзя редактировать после {DEADLINE_TIME.strftime("%H:%M")}',
            push_url=False,
            re_target='#errorBlock',
            re_swap='innerHTML',
        )

    if any([form['first_dish'], form['second_dish_first_part'], form.get('second_dish_second_part')]):
        if order:
            order.date = order_date
            order.comment = form.get('comment', '')
            OrderManager(order=order).clear_dishes()
        else:
            order = entities.Order(
                id=None,
                date=order_date,
                user_id=request.user.id if not anonymous else None,
                comment=form.get('comment', ''),
            )
        OrderManager(order=order).save()

        dishes_ids = [form['first_dish'], form['second_dish_first_part'], form.get('second_dish_second_part')]
        dishes = [DishManager().get_by_id(int(i)) for i in dishes_ids if i]
        OrderManager(order=order).add_dishes(dishes=dishes)

        context['updated_order'] = order
    elif order:
        OrderManager(order).delete()

    if is_admin:
        orders_count = OrderManager().get_count()
        orders = OrderManager().get_all(page=page, per_page=consts.ORDERS_PER_PAGE)
    else:
        orders_count = OrderManager().get_count(user_id=request.user.id)
        orders = OrderManager().get_by_user_id(user_id=request.user.id, page=page, per_page=consts.ORDERS_PER_PAGE)

    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': DishManager().get_by_order_id(order.id),
        }
        for order in orders
    ]

    context.update(
        {
            'orders': page_orders,
            'page': page,
            'pages_count': ceil(orders_count / consts.ORDERS_PER_PAGE) or 1,
        }
    )

    template_name = 'orders.html' if is_admin else 'lunch-block.html'

    return HTMXTemplate(template_name=template_name, context=context, push_url=False)


@post(path='/cancel-order')
async def cancel_order(order_id: int) -> Redirect:
    order = OrderManager().get_by_id(order_id=order_id)
    OrderManager(order=order).delete()

    return Redirect('/my-orders')
