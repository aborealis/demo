#!/bin/sh
# Выполняется в контейнере haystack

FIRST_COMMIT="initial_schema"
APP_FILE="app.py"
FASTAPI_HOST="0.0.0.0"
FASTAPI_PORT="80"
WORKDIR="/code"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-1}"

cd $WORKDIR

# ------------------------
# 1️⃣ Инициализация Alembic
# ------------------------
if [ "$RUN_MIGRATIONS" = "1" ]; then
    if [ ! -d "db/alembic" ]; then
        echo "Alembic не найден. Инициализируем..."
        alembic init db/alembic

        # Перезаписываем конфиг-файл
        cp /root/alembic_env.py db/alembic/env.py

        # Инициируем БД
        ./manage.py makemigrations ${FIRST_COMMIT}
        sed -i '1i import sqlmodel' db/alembic/versions/0001_${FIRST_COMMIT}.py
    fi

    echo "Применение миграций..."
    ./manage.py migrate

    echo "Создание тестовой базы"
    PGPASSWORD="$POSTGRES_PASSWORD" \
    psql -h postgres \
        -U "$POSTGRES_USER" \
        -d postgres \
        -c "CREATE DATABASE tests;"
fi


exec "$@"
