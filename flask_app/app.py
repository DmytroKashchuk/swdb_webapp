"""Simple Flask data explorer for the SWDB PostgreSQL dataset."""

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from psycopg import OperationalError
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()


ALLOWED_PREFIXES = ("select", "with", "show", "describe", "explain")
MAX_ROWS = 500
SAMPLE_QUERIES = [
	"SELECT * FROM usa_2009_hist2009_system LIMIT 25;",
	"SELECT siteid, metro_name, sic2_desc FROM usa_2009_hist2009_literals LIMIT 25;",
	"SELECT corpid, ccompany, sales FROM usa_2009_hist2009_corp ORDER BY sales DESC LIMIT 25;",
]


class QueryValidationError(ValueError):
	"""Custom error when the submitted SQL query is not allowed."""


def create_app() -> Flask:
	app = Flask(__name__)
	pool = _create_connection_pool()

	@app.get("/")
	def index() -> str:
		return render_template("index.html", sample_queries=SAMPLE_QUERIES, max_rows=MAX_ROWS)

	@app.post("/api/run-query")
	def run_query() -> Any:
		payload = request.get_json(silent=True) or {}
		query: str = (payload.get("query") or "").strip()

		try:
			sanitized_query = _validate_query(query)
		except QueryValidationError as exc:
			return jsonify({"error": str(exc)}), 400

		start = time.perf_counter()
		try:
			with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
				cur.execute(sanitized_query)
				rows = cur.fetchmany(MAX_ROWS + 1)
				column_names = [desc[0] for desc in cur.description] if cur.description else []
		except OperationalError:  # database unavailable
			return jsonify({"error": "Database connection failed. Please verify credentials and try again."}), 503
		except Exception as exc:  # pylint: disable=broad-except
			return jsonify({"error": f"Query failed: {exc}"}), 400

		elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
		truncated = len(rows) > MAX_ROWS
		visible_rows = [dict(row) for row in rows[:MAX_ROWS]]
		columns = column_names

		return (
			jsonify(
				{
					"columns": columns,
					"rows": visible_rows,
					"row_count": len(visible_rows),
					"truncated": truncated,
					"elapsed_ms": elapsed_ms,
				}
			),
			200,
		)

	return app


def _create_connection_pool() -> ConnectionPool:
	conninfo = " ".join(
		[
			f"host={os.environ.get('SWDB_DB_HOST', 'localhost')}",
			f"port={os.environ.get('SWDB_DB_PORT', '5432')}",
			f"dbname={os.environ.get('SWDB_DB_NAME', 'swdb')}",
			f"user={os.environ.get('SWDB_DB_USER', 'postgres')}",
			f"password={os.environ.get('SWDB_DB_PASSWORD', '')}",
		]
	)

	return ConnectionPool(conninfo=conninfo, min_size=1, max_size=5, kwargs={"autocommit": True})


def _validate_query(query: str) -> str:
	if not query:
		raise QueryValidationError("Please enter a SQL statement.")

	sanitized = query.rstrip(";\n ")
	lowered = sanitized.lstrip().lower()
	if not lowered.startswith(ALLOWED_PREFIXES):
		allowed = ", ".join(ALLOWED_PREFIXES)
		raise QueryValidationError(f"Only read-only statements are allowed ({allowed}).")

	if _contains_unquoted_semicolon(sanitized):
		raise QueryValidationError("Multiple statements are not allowed.")

	return sanitized


def _contains_unquoted_semicolon(sql: str) -> bool:
	in_single = False
	in_double = False
	i = 0
	while i < len(sql):
		char = sql[i]
		if char == "'" and not in_double:
			if in_single and i + 1 < len(sql) and sql[i + 1] == "'":
				i += 2
				continue
			in_single = not in_single
		elif char == '"' and not in_single:
			if in_double and i + 1 < len(sql) and sql[i + 1] == '"':
				i += 2
				continue
			in_double = not in_double
		elif char == ";" and not in_single and not in_double:
			return True
		i += 1
	return False


app = create_app()


if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8888)))
