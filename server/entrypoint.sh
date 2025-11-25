#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL (Neon / any remote DB)
if command -v pg_isready &> /dev/null; then
    until pg_isready -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}"; do
        echo "Waiting for PostgreSQL..."
        sleep 2
    done
else
    echo "Warning: pg_isready not found, proceeding anyway..."
    sleep 5
fi

echo "PostgreSQL is ready!"

# Run Django migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn on Render's port using the active Python environment
echo "Starting Gunicorn server..."
# NOTE: replace `yourproject.wsgi` with your real WSGI module, e.g. `core.wsgi` or `config.wsgi`
exec python -m gunicorn yourproject.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3