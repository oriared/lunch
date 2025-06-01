import datetime
from math import ceil

from core import entities
from core.consts import DEADLINE_TIME, DishMode
from core.repositories import DishRepo, OrderRepo, UserRepo
from core.services import calendar, dish
from litestar import get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.exceptions import NotFoundException
from litestar.response import Redirect
from sqlalchemy.ext.asyncio import AsyncSession

from web import consts
from web.views.utils import get_selected_date_for_order_form


@get(path='/my-orders')
async def my_orders(request: HTMXRequest, db_session: AsyncSession, page: int = 1) -> HTMXTemplate:
    orders_count = await OrderRepo(session=db_session).get_user_orders_count(user_id=request.user.id)
    orders = await OrderRepo(session=db_session).get_by_user_id(
        user_id=request.user.id, page=page, per_page=consts.ORDERS_PER_PAGE
    )
    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': ', '.join(
                dish.name for dish in await DishRepo(session=db_session).get_by_order_id(order.id)
            ).capitalize(),
        }
        for order in orders
    ]
    today = datetime.date.today()
    context = {
        'orders': page_orders,
        'today': today,
        'isoweekday': today.isoweekday(),
        'selected_module': 'my-orders',
        'page': page,
        'pages_count': ceil(orders_count / consts.ORDERS_PER_PAGE) or 1,
    }
    return HTMXTemplate(template_name='lunch-block.html', context=context, push_url=False)


@get(path='/order-form')
async def order_form(
    request: HTMXRequest,
    db_session: AsyncSession,
    order_id: int | None = None,
    order_date: datetime.date | None = None,
    is_admin: bool = False,
    anonymous: bool = False,
) -> HTMXTemplate:
    date_choices = calendar.get_dates_available_for_making_order()
    order = await OrderRepo(session=db_session).get_by_id(order_id=order_id) if order_id else None

    selected_date = await get_selected_date_for_order_form(
        db_session=db_session,
        user=request.user if not anonymous else None,
        order=order,
        order_date=order_date,
        date_choices=date_choices,
    )
    if not selected_date:
        raise NotFoundException('Нет доступных дат для заказа')

    if not order and not anonymous:
        user_orders = await OrderRepo(session=db_session).get_by_user_id_and_date(
            date=selected_date, user_id=request.user.id
        )
        if user_orders:
            order = user_orders[0]

    context = {
        'isoweekday': selected_date.isoweekday(),
        'selected_module': 'order-form',
        'date_choices': date_choices,
        'dishes': await DishRepo(session=db_session).get_first_dishes(),
        'second_dishes': await DishRepo(session=db_session).get_standard_second_dishes(),
        'second_dishes_first_part': await DishRepo(session=db_session).get_constructor_second_dishes_first_part(),
        'second_dishes_second_part': await DishRepo(session=db_session).get_constructor_second_dishes_second_part(),
        'selected_date': selected_date,
        'selected_dish_mode': DishMode.STANDARD,
        'is_admin': is_admin,
        'anonymous': anonymous,
        'order_user': await UserRepo(session=db_session).get_by_id(user_id=request.user.id) if not anonymous else None,
    }

    if order:
        selected_second_dish_first_part = await DishRepo(session=db_session).get_order_second_dish_first_part(
            order_id=order.id
        )
        selected_second_dish_second_part = await DishRepo(session=db_session).get_order_second_dish_second_part(
            order_id=order.id
        )
        if selected_second_dish_first_part:
            dish_mode = await dish.get_dish_mode(db_session=db_session, dish=selected_second_dish_first_part)
        elif selected_second_dish_second_part:
            dish_mode = DishMode.CONSTRUCTOR
        else:
            dish_mode = DishMode.STANDARD

        context.update(
            {
                'order': order,
                'selected_first_dish': await DishRepo(session=db_session).get_order_first_dish(order_id=order.id),
                'selected_second_dish': await DishRepo(session=db_session).get_order_second_dish(order_id=order.id),
                'selected_second_dish_first_part': selected_second_dish_first_part,
                'selected_second_dish_second_part': selected_second_dish_second_part,
                'selected_dish_mode': dish_mode,
                'comment': order.comment,
                'order_user': await UserRepo(session=db_session).get_by_id(user_id=order.user_id)
                if order.user_id
                else None,
            }
        )

    return HTMXTemplate(template_name='lunch-block.html', context=context, push_url=False)


@get(path='/first-dishes')
async def first_dishes(date: datetime.date, db_session: AsyncSession, vegan: bool | None = None) -> HTMXTemplate:
    dishes = (
        await DishRepo(session=db_session).get_vegan_dishes()
        if vegan
        else await DishRepo(session=db_session).get_first_dishes()
    )
    return HTMXTemplate(
        template_name='first-dishes.html', context={'dishes': dishes, 'isoweekday': date.isoweekday()}, push_url=False
    )


@get(path='/second-dishes')
async def second_dishes(date: datetime.date, dish_mode: str, db_session: AsyncSession) -> HTMXTemplate:
    context = {'selected_dish_mode': dish_mode, 'isoweekday': date.isoweekday()}
    if dish_mode == DishMode.STANDARD:
        context['second_dishes'] = await DishRepo(session=db_session).get_standard_second_dishes()
    elif dish_mode == DishMode.CONSTRUCTOR:
        context['second_dishes_first_part'] = await DishRepo(
            session=db_session
        ).get_constructor_second_dishes_first_part()
        context['second_dishes_second_part'] = await DishRepo(
            session=db_session
        ).get_constructor_second_dishes_second_part()
    return HTMXTemplate(template_name='second-dishes.html', context=context, push_url=False)


@post(path='/save-order')
async def save_order(
    request: HTMXRequest,
    db_session: AsyncSession,
    order_id: int | None = None,
    is_admin: bool = False,
    anonymous: bool = False,
    page: int = 1,
) -> HTMXTemplate:
    form = await request.form()

    today = datetime.date.today()
    context: dict = {
        'today': today,
        'isoweekday': today.isoweekday(),
        'selected_module': 'my-orders',
    }

    order = await OrderRepo(session=db_session).get_by_id(order_id=order_id) if order_id else None
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
            await OrderRepo(session=db_session, order=order).clear_dishes()
        else:
            order = entities.Order(
                id=None,
                date=order_date,
                user_id=request.user.id if not anonymous else None,
                comment=form.get('comment', ''),
            )
        order = await OrderRepo(session=db_session, order=order).save()

        dishes_ids = [
            i for i in (form['first_dish'], form['second_dish_first_part'], form.get('second_dish_second_part')) if i
        ]
        await OrderRepo(session=db_session, order=order).add_dishes(dishes_ids=dishes_ids)

        context['updated_order'] = order
    elif order:
        await OrderRepo(session=db_session, order=order).delete()

    if is_admin:
        orders_count = await OrderRepo(session=db_session).get_count()
        orders = await OrderRepo(session=db_session).get_all(page=page, per_page=consts.ORDERS_PER_PAGE)
    else:
        orders_count = await OrderRepo(session=db_session).get_user_orders_count(user_id=request.user.id)
        orders = await OrderRepo(session=db_session).get_by_user_id(
            user_id=request.user.id, page=page, per_page=consts.ORDERS_PER_PAGE
        )

    page_orders = [
        {
            'id': order.id,
            'date': order.date,
            'comment': order.comment,
            'dishes': ', '.join(
                dish.name for dish in await DishRepo(session=db_session).get_by_order_id(order.id)
            ).capitalize(),
            'user': await UserRepo(session=db_session).get_by_id(order.user_id),
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
async def cancel_order(order_id: int, db_session: AsyncSession) -> Redirect:
    order = await OrderRepo(session=db_session).get_by_id(order_id=order_id)
    await OrderRepo(session=db_session, order=order).delete()
    await db_session.commit()

    return Redirect('/my-orders')
