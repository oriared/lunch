from pathlib import Path

from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.contrib.htmx.request import HTMXRequest
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

from project.views import base, htmx_blocks


static_files_handler = create_static_files_router(path='/static', directories=[Path('project/static')], name='static')

route_handlers = [
    base.index,
    htmx_blocks.order_form,
    htmx_blocks.empty_order_block,
    htmx_blocks.first_dishes,
    htmx_blocks.second_dishes,
    htmx_blocks.save_order,
    static_files_handler,
]

template_config = TemplateConfig(directory=Path('project/templates'), engine=JinjaTemplateEngine)


app = Litestar(
    route_handlers=route_handlers,
    request_class=HTMXRequest,
    template_config=template_config,
)
