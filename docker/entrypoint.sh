#!/bin/sh
set -e

# --- 1. Создаём пользователя django, если его нет ---
if ! id -u django > /dev/null 2>&1; then
    echo "Creating user django..."
    groupadd -r django && useradd -r -g django django
fi

# --- 2. Ждём PostgreSQL ---
echo "Waiting for PostgreSQL..."
while ! nc -z -w 1 $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.5
done
echo "PostgreSQL started"

# --- 3. Ждём Redis ---
echo "Waiting for Redis..."
while ! nc -z -w 1 $REDIS_HOST $REDIS_PORT; do
  sleep 0.5
done
echo "Redis started"

# --- 4. Миграции и сбор статики ---
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# --- 5. Запуск приложения от django ---
exec gosu django "$@"