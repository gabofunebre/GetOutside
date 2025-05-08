@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

set CMD=%1
shift
set MSG=%*

if "%CMD%"=="up" (
    docker compose up --build -d
) else if "%CMD%"=="down" (
    docker compose down
) else if "%CMD%"=="down-volumes" (
    docker compose down -v
) else if "%CMD%"=="rebuild" (
    docker compose down -v
    docker compose up --build -d
) else if "%CMD%"=="ps" (
    docker compose ps
) else if "%CMD%"=="logs-web" (
    docker compose logs -f web
) else if "%CMD%"=="logs-db" (
    docker compose logs -f db
) else if "%CMD%"=="db-psql" (
    docker compose exec db psql -U %DB_USER% -d %DB_NAME%
) else if "%CMD%"=="push" (
    git add .
    git commit -m "%MSG%"
    git push
) else (
    echo Comando no reconocido: %CMD%
)

ENDLOCAL
