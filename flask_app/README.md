# SWDB Query Explorer

A minimal Flask + Tabulator web app for running **read-only** SQL queries against the `swdb` PostgreSQL database and visualising the results in a responsive table.

## Prerequisites

- Python 3.9+
- Access to the PostgreSQL instance described in `.github/instructions/postgressql_connection.md`

## Installation

Create and activate a virtual environment (recommended), then install dependencies:

```bash
pip install flask psycopg2-binary
```

## Running the app

From the `flask_app` folder:

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5000/
```

## Usage

1. Type or edit a **SELECT** query in the SQL box at the top of the page.
2. Click **Run query**.
3. The results will appear in the Tabulator table below.
   - Columns are resizable and movable.
   - The table supports horizontal scrolling to accommodate many columns.

> Note: Only `SELECT` queries are allowed for safety; other statement types will be rejected.
