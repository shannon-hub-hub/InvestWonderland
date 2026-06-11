#!/bin/sh
set -eu
cd /app
exec python scripts/run_ingestion.py --source all
