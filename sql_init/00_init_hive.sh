#!/bin/bash
set -e

echo "Creating samples table..."
mysql -u root -p"$MYSQL_ROOT_PASSWORD" hive < /docker-entrypoint-initdb.d/definitions/samples_definition.sql

echo "Importing hive_wo_samples.dmp.gz..."
zcat /docker-entrypoint-initdb.d/hive_wo_samples.dmp.gz | mysql -u root -p"$MYSQL_ROOT_PASSWORD" hive

echo "Importing samples_monthly_dump_2024-05.bkp.gz..."
zcat /docker-entrypoint-initdb.d/samples_monthly_dump_2024-05.bkp.gz | mysql -u root -p"$MYSQL_ROOT_PASSWORD" hive

echo "Importing samples_monthly_dump_2024-06.bkp.gz..."
zcat /docker-entrypoint-initdb.d/samples_monthly_dump_2024-06.bkp.gz | mysql -u root -p"$MYSQL_ROOT_PASSWORD" hive

echo "Importing samples_monthly_dump_2024-07.bkp.gz..."
zcat /docker-entrypoint-initdb.d/samples_monthly_dump_2024-07.bkp.gz | mysql -u root -p"$MYSQL_ROOT_PASSWORD" hive

echo "Hive database initialization complete."
