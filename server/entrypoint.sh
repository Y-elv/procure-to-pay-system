#!/usr/bin/env bash
set -e

echo "Waiting for PostgreSQL to be ready..."

if command -v pg_isready &> /dev/null; then
  until pg_isready -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}"; do
    echo "Waiting for PostgreSQL..."
    sleep 2
  done
else
  echo "Warning: pg_isready not found, proceeding after short wait..."
  sleep 5
fi

echo "PostgreSQL is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Determine WSGI module:
# Priority: WSGI_MODULE env var -> derived from DJANGO_SETTINGS_MODULE -> fallback to config.wsgi
if [ -z "${WSGI_MODULE:-}" ]; then
  if [ -n "${DJANGO_SETTINGS_MODULE:-}" ]; then
    WSGI_MODULE="${DJANGO_SETTINGS_MODULE%.*}.wsgi"
  else
    # try to parse manage.py for DJANGO_SETTINGS_MODULE
    DJANGO_SETTINGS_MODULE=$(python - <<'PY'
import re
try:
    text = open("manage.py").read()
    m = re.search(r"DJANGO_SETTINGS_MODULE'\s*,\s*'([^']+)'", text) or re.search(r'DJANGO_SETTINGS_MODULE\"\s*,\s*\"([^"]+)\"', text)
    if m:
        print(m.group(1))
except Exception:
    pass
PY
)
    if [ -n "${DJANGO_SETTINGS_MODULE}" ]; then
      WSGI_MODULE="${DJANGO_SETTINGS_MODULE%.*}.wsgi"
    fi
  fi
fi

# Fallback if detection failed
: "${WSGI_MODULE:=config.wsgi}"

echo "Starting Gunicorn server using WSGI module: ${WSGI_MODULE}"
exec python -m gunicorn "${WSGI_MODULE}:application" --bind 0.0.0.0:${PORT:-8000} --workers 3