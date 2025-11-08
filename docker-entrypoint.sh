#!/bin/sh
set -eu

alembic upgrade head
python scripts/seed_data.py

exec "$@"
