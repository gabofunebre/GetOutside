# Detecta el binario de Docker y Compose
DOCKER := $(shell command -v docker)
COMPOSE := $(DOCKER) compose

# Declaración de comandos que no generan archivos
.PHONY: up down up-prod down-prod down-prod-volumes logs-web logs-db push branch checkout new-branch pull status log

# === Entorno de desarrollo ===

# Levanta solo el contenedor web de desarrollo
up:
	$(COMPOSE) -p getoutside_dev -f docker-compose.yml -f docker-compose.override.yml up --build -d


# Baja el contenedor web de desarrollo
down:
	$(COMPOSE) -f docker-compose.yml down

# ===================================================
# ===================================================
# ===================================================

# === Entorno de producción ===

# Levanta contenedores web y db de producción
up-prod:
	$(COMPOSE) -f docker-compose.prod.yml up --build -d

# Baja contenedores de producción sin borrar volúmenes
down-prod:
	$(COMPOSE) -f docker-compose.prod.yml down

# Baja contenedores de producción y elimina volúmenes (base de datos)
down-prod-volumes:
	$(COMPOSE) -f docker-compose.prod.yml down -v

# ===================================================
# ===================================================
down-all:
	down down-prod
# ===================================================

# === Logs ===

# Muestra logs del contenedor web
logs-web:
	$(COMPOSE) -p getoutside_dev logs -f web

	# Produccion
logs-web-prod:
	$(COMPOSE) logs -f web

# Muestra logs del contenedor db (solo en producción)
logs-db:
	$(COMPOSE) logs -f db


# ===================================================
# ===================================================
# ===================================================

# === Git ===

# Despliega en producción (pull + up-prod)
deploy-prod:
	@if [ "$$(git branch --show-current)" != "prod" ]; then \
		echo "⚠️  Estás en una rama distinta a 'prod'. Abortando..."; \
		exit 1; \
	fi
	git pull origin prod
	$(MAKE) up-prod

# Commit y push con mensaje: make push "mensaje"
push:
	@$(eval MSG := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(MSG)" ]; then \
		echo 'Uso: make push \"Mensaje de commit\"'; \
		exit 1; \
	fi
	git add .
	git commit -m "$(MSG)"
	git push -u origin HEAD

# Muestra la rama actual
branch:
	git branch --show-current

# Cambia a una rama existente: make checkout nombre_rama
checkout:
	@$(eval BR := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(BR)" ]; then \
		echo 'Uso: make checkout nombre_rama'; \
		exit 1; \
	fi
	git checkout $(BR)

# Crea y cambia a una nueva rama: make new-branch nombre_rama
new-branch:
	@$(eval BR := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(BR)" ]; then \
		echo 'Uso: make new-branch nombre_rama'; \
		exit 1; \
	fi
	git checkout -b $(BR)

# Hace pull de la rama actual
pull:
	git pull

# Muestra el estado del repo
status:
	git status

# Muestra el historial con gráfico
log:
	git log --oneline --graph --decorate --all

# Necesario para evitar errores con argumentos como "make push mensaje"
%:
