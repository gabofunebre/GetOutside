#!/usr/bin/env bash
# wait-for-db.sh
set -e

host="$DB_HOST"
port="$DB_PORT"

>&2 echo "Esperando a que la base de datos $host:$port esté disponible..."
while ! nc -z "$host" "$port"; do
  sleep 1
  >&2 echo "Esperando a que la base de datos $host:$port esté disponible..."
done

>&2 echo "Base de datos disponible, arrancando aplicación..."

if [ "$APP_ENV" = "development" ]; then
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
