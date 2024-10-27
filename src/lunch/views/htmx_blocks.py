from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar import get, post
from litestar.response import Template

from database import queries
import dto


@get(path='/users')
async def users() -> HTMXTemplate:
    context = {'users': queries.get_users()}
    return HTMXTemplate(template_name='users.html', context=context, push_url=False)


@get(path='/order-form')
async def order_form() -> Template:
    context = {
        'dishes': queries.first_dishes(),
        'second_dishes': queries.get_standard_second_dishes(),
    }
    return HTMXTemplate(template_name='order-form.html', context=context, push_url=False)


@get(path='/empty-order-block')
async def empty_order_block() -> Template:
    return HTMXTemplate(template_name='empty-order-block.html', push_url=False)


@get(path='/first-dishes')
async def first_dishes(vegan: str | None = None) -> Template:
    dishes = queries.get_vegan_dishes() if vegan else queries.first_dishes()
    return HTMXTemplate(template_name='first-dishes.html', context={'dishes': dishes}, push_url=False)


@get(path='/second-dishes')
async def second_dishes(dish_mode: str) -> Template:
    context = {'mode': dish_mode}
    if dish_mode == 'standard':
        context['second_dishes'] = queries.get_standard_second_dishes()
    elif dish_mode == 'constructor':
        context['second_dishes_first_part'] = queries.get_constructor_second_dishes(part='first')
        context['second_dishes_second_part'] = queries.get_constructor_second_dishes(part='second')
    return HTMXTemplate(template_name='second-dishes.html', context=context, push_url=False)


@post(path='/save-order')
async def save_order(request: HTMXRequest) -> Template:
    form = await request.form()
    lunch = dto.Lunch(**form)
    order = queries.save_order(lunch)
    return HTMXTemplate(template_name='save-order.html', push_url=False)
