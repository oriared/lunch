from litestar import get
from litestar.response import Template


@get(path='/')
async def index() -> Template:
    return Template(template_name='index.html')
