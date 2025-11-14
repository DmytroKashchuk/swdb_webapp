#!/usr/bin/env bash
set -euo pipefail

cd /home/dima/swdb_webapp

DB_NAME="swdb"
DB_USER="postgres_dima"
DB_HOST="localhost"
DB_PASS="Dadomagico96!"   # optional: set in env or inline

# Expect: ./execute_upload_queries.sh <region> <year>
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <region> <year>"
  echo "Example: $0 usa 2017"
  exit 1
fi

REGION_RAW="$1"
YEAR="$2"

# Normalise region to lowercase to match folder naming like usa_2017, emea_2017, etc.
REGION="$(echo "$REGION_RAW" | tr '[:upper:]' '[:lower:]')"
TARGET_DIR="automate_upload/${REGION}_${YEAR}"

if ! compgen -G "${TARGET_DIR}/*.sql" > /dev/null; then
  echo "No .sql files found in ${TARGET_DIR}"
  exit 1
fi

for f in "${TARGET_DIR}"/*.sql; do
  echo "Running load file: $f"
  if [[ -n "$DB_PASS" ]]; then
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
  else
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
  fi
done