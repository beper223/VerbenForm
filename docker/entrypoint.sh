#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z -w 1 $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.5
done

echo "PostgreSQL started"

# Права на static
mkdir -p /app/staticfiles /app/logs
if [ "$(stat -c '%U:%G' /app/staticfiles)" != "django:django" ]; then
    chown -R django:django /app/staticfiles /app/logs
fi

# Миграции
python manage.py migrate --noinput

# Сбор статики
python manage.py collectstatic --noinput

exec gosu django "$@"
