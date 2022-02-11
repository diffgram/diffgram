#!/bin/sh
# db-init.sh

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$DATABASE_PASS psql -h "$host" -d "$DATABASE_NAME" -U "$DATABASE_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

cd shared; alembic upgrade head
>&2 echo "Postgres is up - executing command"
exec $cmd