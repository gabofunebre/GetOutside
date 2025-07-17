# GetOutside Stock App

Simple web app to manage product catalog, stock, sales, payments and basic metrics.

## Quickstart

1. Copy your `.env` with your DB credentials:
   ```bash
   cp .env.example .env
   # edit .env: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY
   ```

2. Build & run with Docker Compose (includes a local Postgres container):
   ```bash
   make up        # builds images and starts containers
   ```

3. Visit in your browser:
   - Dashboard → `http://localhost:14141/`
   - Add products → `/productos/new`
   - Register sales → `/ventas/new`
   - Admin → `/admin`
   - Consults → `/consultas`
   - Metrics → `/metrics`

Database files are stored under `./data/db`, so your data persists even if you
rebuild the containers.  Code is mounted with live reload so changes to `.py`
and template files are reflected immediately.

4. To tear down (including DB data):
   ```bash
   make down-volumes
   ```

## Commands

- `make up` / `make rebuild` / `make down(-volumes)`  
- `make logs-web` / `make logs-db`  
- `make db-psql`



En resumen
Routers: “Qué quiero hacer y con qué datos”.

CRUD: “Cómo lo hago en la base de datos”.

Modelos: “Cómo es la base”.

Schemas: “Cómo se ve la información que entra y sale”.