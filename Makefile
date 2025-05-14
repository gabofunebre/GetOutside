# Makefile para gestión de contenedores Docker Compose y Git

# buscamos el binario de docker en PATH, para usar ruta absoluta
DOCKER := $(shell command -v docker)
# si no lo encuentra, fallará al ejecutar
COMPOSE := $(DOCKER) compose

.PHONY: up down down-volumes rebuild ps logs-web logs-db db-psql push

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

down-volumes:
	$(COMPOSE) down -v

rebuild: down-volumes up

ps:
	$(COMPOSE) ps

logs-web:
	$(COMPOSE) logs -f web

logs-db:
	$(COMPOSE) logs -f db

db-psql:
	$(COMPOSE) exec db psql -U $$(echo "$$DB_USER") -d $$(echo "$$DB_NAME")

# push: añade todos los cambios, hace commit con el mensaje
# Uso: make push "Mensaje de commit"
push:
	@$(eval MSG := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(MSG)" ]; then \
		echo 'Uso: make push "Mensaje de commit"'; \
		exit 1; \
	fi
	git add .
	git commit -m "$(MSG)"
	git push -u origin main

# evita errores por objetivos extra (como el mensaje de commit)
%:
