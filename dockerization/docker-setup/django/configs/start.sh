#!/bin/bash

MYPROJECT=mysite

# Check MariaDB availability
echo "Checking MariaDB availability..."
until mysqladmin ping -h mariadb -u root -p$MARIADB_ROOT_PASSWORD --silent; do
    echo "MariaDB is not yet available. Retrying in 1 seconds..."
    sleep 1
done

echo "MariaDB is available! Starting Django..."

# We additionally write errors into the file on the mounted volume
exec gunicorn ${MYPROJECT}.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind unix:/run/socket/gunicorn.sock \
    --workers $(( $(nproc) * 2 + 1 )) \
    --access-logfile - \
    --error-logfile /code/gunicorn-error.log \
    --log-level error