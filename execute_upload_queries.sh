cd /Users/dmk6603/Documents/swdb_webapp

DB_NAME="swdb"
DB_USER="dima"
DB_HOST="localhost"

for f in automate_upload/usa_2017/*.sql; do
  echo "Running load file: $f"
  psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
done
