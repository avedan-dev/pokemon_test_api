all:
		@echo "make venv		- Создает и настраивает вирутальное окружение для проекта"
		@echo "make lint		- Проверка кода на PEP"
		@echo "make start		- Создает и запускает все необходимые контейнеры для приложения"
		@echo "make web		- Собирает и запускает контейнер web приложения"
		@echo "make db			- Собирает и запускает контейнер базы данных"
		@echo "make nginx		- Собирает и запускает контейнер nginx"
		@echo "make test		- Запустить тесты"
		@echo "make stop		- Oстанавливает все контейнеры"
		@echo "make run-local	- Запускает локальный сервер"
		@exit 0

venv:
	python -m venv venv
	./venv/bin/python -m pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt


lint:
	venv/bin/pylama

test:
	venv/bin/pytest

db:
	docker-compose up -d db

nginx:
	docker-compose up -d nginx

stop:
	docker-compose down -v

start:
	docker-compose up -d

run-local:
	python manage.py runserver
