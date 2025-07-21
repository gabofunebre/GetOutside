# GetOutside Stock App

Simple web app to manage product catalog, stock, sales, payments and basic metrics.

## Quickstart

1. Copy your `.env` with your DB credentials:
   ```bash
   cp .env.example .env
   # edit .env: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY
   ```

2. Build & run with Docker Compose:
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

4. To tear down (including DB data):
   ```bash
   make down-volumes
   ```

## Google OAuth

1. Crea un **cliente OAuth 2.0** en la consola de Google y anota el `ID de cliente` y `secreto`.
2. Agrega la URL de callback en el cliente (por ejemplo `http://localhost:14141/auth/google/callback`).
3. Copia esos valores en tu archivo `.env` usando las claves `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `GOOGLE_REDIRECT_URI`.
4. Inicia la aplicación y podrás ingresar o registrarte con Google desde la pantalla de login.

## Commands

- `make up` / `make rebuild` / `make down(-volumes)`  
- `make logs-web` / `make logs-db`  
- `make db-psql`



En resumen
Routers: “Qué quiero hacer y con qué datos”.

CRUD: “Cómo lo hago en la base de datos”.

Modelos: “Cómo es la base”.

Schemas: “Cómo se ve la información que entra y sale”.