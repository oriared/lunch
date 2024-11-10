# Веб-приложение для заказа обедов

 - litestar
 - jinja2
 - HTMX

Установка с [uv](https://github.com/astral-sh/uv):

1. Клонировать проект
2. Перейти в директорию проекта
3. `uv venv`
4. `source .venv/bin/Activate`
5. `uv sync`

 - Если PyCharm не видит импорты библиотек - поменять окружение: Settings -> Project -> Python Interpreter -> Add -> Existing -> Интерпретатор из директории .venv данного проекта

Запуск:

1. `cd src/lunch`
2. `uv run litestar run`
   
   [Документация litestar: команда run](https://docs.litestar.dev/2/reference/cli.html#litestar-run)
