# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar netcat para wait-for-db.sh
RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait-for-db.sh

CMD ["./wait-for-db.sh"]
