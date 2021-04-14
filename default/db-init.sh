#!/bin/sh
# db-init.sh

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

cd shared; alembic upgrade head
>&2 echo "Postgres is up - executing command"
exec $cmd