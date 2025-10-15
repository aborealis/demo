#!/bin/bash

max_retries=300
retry_interval=1

for ((retry=1; retry<=$max_retries; retry++))
do
    if mysqladmin ping -h mariadb -u "$MARIADB_USER" -p"$MARIADB_PASSWORD" --silent; then
        exit 0
    fi

    echo "MariaDB is not yet available. Retrying in $retry_interval seconds..."
    sleep $retry_interval
done

echo "Unable to connect to MariaDB"
exit 1

