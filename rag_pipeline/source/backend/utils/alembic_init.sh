#!/bin/sh
# restored comment from original Russian source

set -e  # fail fast

APP_FILE="app.py"
FASTAPI_HOST="0.0.0.0"
FASTAPI_PORT="80"
WORKDIR="/code"

cd $WORKDIR

# ------------------------
# restored comment from original Russian source
# ------------------------
if [ ! -d "alembic" ] || [ ! -f "alembic.ini" ]; then
    echo "Alembic is not initialized. Creating scaffold..."
    alembic init db/alembic

    # restored comment from original Russian source
    cp /root/alembic_env.py db/alembic/env.py
fi
