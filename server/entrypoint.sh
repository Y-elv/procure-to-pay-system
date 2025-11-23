#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."
# Wait for PostgreSQL (using pg_isready if available, otherwise skip)
if command -v pg_isready &> /dev/null; then
    until pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do
        echo "Waiting for PostgreSQL..."
        sleep 1
    done
elif command -v nc &> /dev/null; then
    until nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        echo "Waiting for PostgreSQL..."
        sleep 1
    done
else
    echo "Warning: Cannot check PostgreSQL readiness. Proceeding anyway..."
    sleep 5
fi

echo "PostgreSQL is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
# python manage.py shell << EOF
# from core.models import User
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='finance')
# EOF

# Start server
echo "Starting Django server..."
exec "$@"

