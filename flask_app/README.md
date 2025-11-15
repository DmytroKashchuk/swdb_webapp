# SWDB Data Explorer

A minimalist Flask interface to explore the SWDB PostgreSQL dataset. The UI lets you
submit read-only SQL queries, view results in a Tabulator grid, and export selections
as CSV or JSON. The layout is intentionally white, full-width, and distraction-free to
match academic usage.

## Prerequisites

- Python 3.10+
- Access to the SWDB PostgreSQL instance (credentials provided separately)

Set the required environment variables before running the app:

```bash
export SWDB_DB_HOST=10.20.5.20
export SWDB_DB_PORT=5432
export SWDB_DB_NAME=swdb
export SWDB_DB_USER=postgres_dima
export SWDB_DB_PASSWORD='<password>'
```

You can also place these in a `.env` file if you prefer using `python-dotenv`.

## Installation & run

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000 to open the explorer.

## Features

- **Guardrails** – only SELECT/WITH/SHOW/DESCRIBE/EXPLAIN statements are accepted and
	multiple statements are blocked.
- **Responsive UI** – Tabulator handles wide tables, sorting, resizing, and local
	filtering while keeping the page clean and fully wide.
- **Exports** – Download visible data as CSV or JSON with a single click.
- **Sample queries** – One-click chips make it easy to start exploring the dataset.

## Next steps

- Add authentication if the explorer is exposed beyond trusted users.
- Persist query history for auditors or teaching assistants.
- Add schema metadata lookup endpoints to provide autocomplete in the editor.
