cd /Users/dmk6603/Documents/swdb_webapp

DB_NAME="swdb"
DB_USER="dima"          # or whatever your postgres user is
DB_HOST="localhost"     # or the right host

for f in automate/usa_2017/*.sql; do
  echo "Running schema file: $f"
  psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
done
