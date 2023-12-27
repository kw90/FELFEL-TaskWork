#!/bin/bash
set -e

./wait-for-it.sh "$POSTGRES_HOST:$POSTGRES_PORT"

exec "$@"
