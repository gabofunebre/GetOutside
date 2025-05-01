# Makefile para gestión de contenedores Docker Compose y Git

.PHONY: up down down-volumes rebuild ps logs-web logs-db db-psql push

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

# push: añade todos los cambios, hace commit con el mensaje
# y hace push. Uso: make push "Mensaje de commit"
push:
	@$(eval MSG := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(MSG)" ]; then \
		echo 'Uso: make push "Mensaje de commit"'; \
		exit 1; \
	fi
	git add .
	git commit -m "$(MSG)"
	git push -u origin main

# Evita errores por objetivos desconocidos (como el mensaje)
%:
