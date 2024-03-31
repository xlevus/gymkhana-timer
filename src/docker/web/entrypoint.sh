#!/bin/bash
set -e

if [ -f "$SECRET_KEY_FILE" ]; then
    export SECRET_KEY=$(cat "$SECRET_KEY_FILE")
fi

if [ -f "$DATABASE_URL_FILE" ]; then
    export DATABASE_URL=$(cat "$DATABASE_URL_FILE")
fi

if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL is unset"
    exit 1
fi

if [ -d "$STATIC_ROOT" ]; then
    echo "Collecting Static"
    /manage.pex collectstatic --noinput
fi

echo "Migrating"
/manage.pex migrate --no-input

echo "Running"
exec /gunicorn.pex