#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head
python scripts/seed_data.py

exec "$@"
