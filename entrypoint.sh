#!/bin/sh
set -e

echo "==> Waiting for database..."
python manage.py wait_for_db

echo "==> Running migrations..."
python manage.py migrate --noinput

if [ "${SEED_DATA:-false}" = "true" ]; then
    echo "==> Seeding database..."
    python manage.py seed_data
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn event_management_system.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
