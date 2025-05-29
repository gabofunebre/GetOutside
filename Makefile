################################################################################
#              Makefile para gestión de GetOutside (Dev y Producción)          #
################################################################################

# === [BINARIOS DOCKER] =======================================================

# Detecta el binario de Docker y Compose
DOCKER := $(shell command -v docker)
COMPOSE := $(DOCKER) compose

# Declaración de comandos que no generan archivos
.PHONY: \
  up down up-prod down-prod down-prod-volumes \
  logs-web logs-web-prod logs-db \
  clean-images clean-all help \
  push branch checkout new-branch pull status log down-all \
  push-to-prod deploy-prod

################################################################################
#                       SECCIÓN: DESARROLLO                                    #
################################################################################

# Levanta solo el contenedor web de desarrollo
up:
	$(COMPOSE) -p getoutside_dev -f docker-compose.yml -f docker-compose.override.yml up --build -d

# Baja el contenedor web de desarrollo
down:
	$(COMPOSE) -p getoutside_dev -f docker-compose.yml -f docker-compose.override.yml down

################################################################################
#                       SECCIÓN: PRODUCCIÓN                                    #
################################################################################

# Levanta contenedores web y db de producción
up-prod:
	$(COMPOSE) -f docker-compose.prod.yml up --build -d

# Baja contenedores de producción sin borrar volúmenes
down-prod:
	$(COMPOSE) -f docker-compose.prod.yml down

# Baja contenedores de producción y elimina volúmenes (base de datos)
down-prod-volumes:
	$(COMPOSE) -f docker-compose.prod.yml down -v

# Baja ambos entornos
down-all:
	$(MAKE) down
	$(MAKE) down-prod

################################################################################
#                       SECCIÓN: LOGS                                          #
################################################################################

# Muestra logs del contenedor web de desarrollo
logs-web:
	$(COMPOSE) -p getoutside_dev logs -f web

# Muestra logs del contenedor web de producción
logs-web-prod:
	$(COMPOSE) logs -f web

# Muestra logs del contenedor db de producción
logs-db:
	$(COMPOSE) logs -f db

################################################################################
#                       SECCIÓN: LIMPIEZA                                      #
################################################################################

# Limpia imágenes Docker sin tag (<none>)
clean-images:
	$(DOCKER) image prune -f

# Limpia TODO lo no usado (imágenes, contenedores parados, redes no usadas, etc.)
clean-all:
	$(DOCKER) system prune -af

################################################################################
#                       SECCIÓN: GIT                                           #
################################################################################

# Commit y push con mensaje: make push "mensaje"
push:
	@$(eval MSG := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(MSG)" ]; then \
		echo 'Uso: make push "Mensaje de commit"'; \
		exit 1; \
	fi
	git add .
	git commit -m "$(MSG)"
	git push -u origin HEAD

# Merge de main en prod con commit personalizado, push y retorno a main
push-to-prod:
	@CURRENT=$$(git branch --show-current); \
	if [ "$$CURRENT" != "main" ]; then \
		echo "⚠️  Esta acción solo se puede ejecutar desde 'main'"; \
		exit 1; \
	fi; \
	read -p "📝 Mensaje de commit para main (ENTER para omitir): " MSG; \
	if [ ! -z "$$MSG" ]; then \
		git add . && git commit -m "$$MSG"; \
	else \
		echo "🔃 Sin commit nuevo en main."; \
	fi; \
	echo "🚀 Cambiando a prod y haciendo merge..."; \
	git checkout prod && \
	git merge main && \
	git push origin prod && \
	echo "✅ Deploy en prod completado. Volviendo a main..."; \
	git checkout main

# Despliega en producción (pull + up-prod)
deploy-prod:
	@if [ "$$(git branch --show-current)" != "prod" ]; then \
		echo "⚠️  Estás en una rama distinta a 'prod'. Abortando..."; \
		exit 1; \
	fi
	git pull origin prod
	$(MAKE) up-prod

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

################################################################################
#                       SECCIÓN: AYUDA                                         #
################################################################################

help:
	@echo ""
	@echo "=====================  Makefile GetOutside  ====================="
	@echo ""
	@echo "Desarrollo:"
	@echo "  make up                  Levanta el contenedor web de desarrollo"
	@echo "  make down                Baja el contenedor web de desarrollo"
	@echo ""
	@echo "Producción:"
	@echo "  make up-prod             Levanta web y db de producción"
	@echo "  make down-prod           Baja web y db de producción (sin borrar volúmenes)"
	@echo "  make down-prod-volumes   Baja web y db de producción y elimina volúmenes (ej: base de datos)"
	@echo ""
	@echo "Limpieza:"
	@echo "  make clean-images        Borra imágenes Docker <none> (no usadas)"
	@echo "  make clean-all           Limpia imágenes, contenedores y redes no usadas"
	@echo ""
	@echo "Logs:"
	@echo "  make logs-web            Logs del web de desarrollo"
	@echo "  make logs-web-prod       Logs del web de producción"
	@echo "  make logs-db             Logs del contenedor db (producción)"
	@echo ""
	@echo "Git:"
	@echo "  make push 'msg'          Commit y push con mensaje"
	@echo "  make push-to-prod        Merge main en prod, push y vuelve a main"
	@echo "  make deploy-prod         Pull en prod y levanta contenedores prod"
	@echo "  make branch              Muestra rama actual"
	@echo "  make checkout rama       Cambia a una rama existente"
	@echo "  make new-branch rama     Crea y cambia a nueva rama"
	@echo "  make pull                Pull de la rama actual"
	@echo "  make status              Estado del repo"
	@echo "  make log                 Log con gráfico"
	@echo ""
	@echo "Varios:"
	@echo "  make down-all            Baja dev y prod"
	@echo ""
	@echo "==============================================================="
	@echo ""

# Para evitar errores con argumentos tipo: make push "mensaje"
%:

################################################################################

db:
	psql -U getoutside -d getoutside_stock -h localhost