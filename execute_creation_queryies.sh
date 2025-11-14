#!/usr/bin/env bash
set -euo pipefail

# Go to project folder
cd /home/dima/swdb_webapp

DB_NAME="swdb"
DB_USER="postgres_dima"
DB_HOST="127.0.0.1"
DB_PASS="Dadomagico96!"   # ⚠️ plain-text; better to use .pgpass in real life

# Usage check
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <region> <year>"
  echo "Example: $0 usa 2017"
  exit 1
fi

REGION_RAW="$1"
YEAR="$2"

# Normalize region (so USA / Usa / usa all work)
REGION="$(echo "$REGION_RAW" | tr '[:upper:]' '[:lower:]')"

# Folder pattern: automate_creation/usa_2017, emea_2016, ...
TARGET_DIR="automate_creation/${REGION}_${YEAR}"

# Check that there are .sql files in that directory
if ! compgen -G "${TARGET_DIR}/*.sql" > /dev/null; then
  echo "No .sql files found in ${TARGET_DIR}"
  exit 1
fi

# Run every .sql file in that folder
for f in "${TARGET_DIR}"/*.sql; do
  echo "Running schema file: $f"
  PGPASSWORD="$DB_PASS" psql \
    -h "$DB_HOST" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -v ON_ERROR_STOP=1 \
    -f "$f"
done