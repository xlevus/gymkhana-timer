#!/bin/bash
set -e

if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL is unset"
    exit 1
fi

echo "Migrating"
/manage.pex migrate --no-input

echo "Running"
exec /gunicorn.pex