# Detectamos binarios
DOCKER := $(shell command -v docker)
COMPOSE := $(DOCKER) compose

# Configuración general
.PHONY: up down down-volumes rebuild rebuild-v ps logs-web logs-db db-psql push dev prod dev-down prod-down dev-logs prod-logs

# Entorno actual (override activo)
up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

down-volumes:
	$(COMPOSE) down -v

rebuild-v: down-volumes up

rebuild: down up

ps:
	$(COMPOSE) ps

logs-web:
	$(COMPOSE) logs -f web

logs-db:
	$(COMPOSE) logs -f db

db-psql:
	$(COMPOSE) exec db psql -U $$(echo "$$DB_USER") -d $$(echo "$$DB_NAME")

# --- Nuevos comandos separados por entorno ---

dev:
	$(COMPOSE) up --build -d

prod:
	$(COMPOSE) -f docker-compose.yml up --build -d

dev-down:
	$(COMPOSE) down

prod-down:
	$(COMPOSE) -f docker-compose.yml down

dev-logs:
	$(COMPOSE) logs -f web

prod-logs:
	$(COMPOSE) -f docker-compose.yml logs -f web

# Git push con mensaje: make push "mensaje"
push:
	@$(eval MSG := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(MSG)" ]; then \
		echo 'Uso: make push "Mensaje de commit"'; \
		exit 1; \
	fi
	git add .
	git commit -m "$(MSG)"
	git push -u origin main

%:
