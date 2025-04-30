# Makefile para gestión de contenedores Docker Compose

.PHONY: up down down-volumes rebuild ps logs-web logs-db db-psql

up:
	docker compose up --build -d

down:
	docker compose down

down-volumes:
	docker compose down -v

rebuild:
	make down-volumes
	make up

ps:
	docker compose ps

logs-web:
	docker compose logs -f web

logs-db:
	docker compose logs -f db

db-psql:
	docker compose exec db psql -U $$(echo "$$DB_USER") -d $$(echo "$$DB_NAME")
