# Веб-приложение для заказа обедов

Установка с [PDM](https://github.com/pdm-project/pdm):

1. Клонировать проект
2. Перейти в директорию проекта
3. `pdm use 3.12`
4. `pdm install`

 - Если PyCharm не видит импорты библиотек - поменять окружение: Settings -> Project -> Python Interpreter -> Add -> Existing -> Интерпретатор из директории .venv данного проекта

Запуск:

1. `cd src/lunch`
2. `pdm run litestar run`
   
   [Документация litestar: команда run](https://docs.litestar.dev/2/reference/cli.html#litestar-run)
