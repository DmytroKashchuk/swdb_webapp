from flask import Flask, render_template, request, jsonify, abort, Response, send_from_directory, redirect, url_for
import markdown
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
import csv
import io
import json
import re
import threading
import pandas as pd
import psycopg2
import psycopg2.extras


app = Flask(__name__)


def get_db_connection():
	"""Create a new database connection.

	NOTE: In a real app you should not hard-code credentials; they are
	inlined here only because this project uses a local, non-production DB
	and provided them in instructions.
	"""

	return psycopg2.connect(
		host="10.20.5.20",
		port=5432,  # "standard" PostgreSQL port
		dbname="swdb",
		user="postgres_dima",
		password="Dadomagico96!",
		# Long-running builds otherwise die with "could not receive data from server".
		keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=10,
	)


@app.route("/")
def index():
	# Default example query; user can overwrite it in the UI
	example_query = "SELECT * FROM usa_2015_hist2015_sitedesc LIMIT 100;"
	return render_template(
		"index.html",
		example_query=example_query,
		default_limit=QUERY_DEFAULT_LIMIT,
		max_limit=QUERY_MAX_LIMIT,
		timeout_s=QUERY_TIMEOUT_MS // 1000,
	)


@app.route("/companies")
def companies():
	"""Companies search page.

	Allows searching by company name, site ID, or URL and year bucket.

	Year buckets map to different underlying tables/columns as provided:
	- 2000/2009: usa_2009_hist2009_sitedesc.company / siteid / homepageurl
	- 2010-2015: usa_2015_hist2015_sitedesc.company / siteid / homepageurl
	- 2016-2020: usa_2016_sitedescription.company / siteid / homepageurl
	- 2020-2022: usa_2022_sites.site_name / site_id / site_url
	"""

	q_value = request.args.get("q", "").strip()
	search_mode = request.args.get("mode", "company")
	year_raw = request.args.get("year")
	hq_only = request.args.get("hq_only") == "on"
	gov_filter = request.args.get("gov_filter") == "on"
	gov_levels = request.args.getlist("gov_levels")

	rows = []
	columns = []
	error = None
	company_searched = bool(q_value)
	selected_year = None

	if q_value and year_raw:
		# Parse chosen year
		try:
			year = int(year_raw)
		except (TypeError, ValueError):
			error = "Year must be a valid number."
		else:
			selected_year = year
			# Choose table and column pattern based on year
			if year in (2000, 2009):
				# 2000 & 2009: usa_[year]_hist[year]_sitedesc
				table = f"usa_{year}_hist{year}_sitedesc"
				company_col = "company"
				siteid_col = "siteid"
				url_col = "homepageurl"
			elif 2010 <= year <= 2015:
				# 2010-2015: usa_[year]_hist[year]_sitedesc
				table = f"usa_{year}_hist{year}_sitedesc"
				company_col = "company"
				siteid_col = "siteid"
				url_col = "homepageurl"
			elif 2016 <= year <= 2020:
				# 2016-2020: usa_[year]_site_description
				table = f"usa_{year}_site_description"
				company_col = "company"
				siteid_col = "siteid"
				url_col = "homepageurl"
			elif 2020 <= year <= 2022:
				# 2020-2022: usa_[year]_sites
				table = f"usa_{year}_sites"
				company_col = "site_name"
				siteid_col = "site_id"
				url_col = "site_url"
			else:
				error = "Year must be between 2000 and 2022."

			if not error:
				# Decide which field to filter on based on search mode
				if search_mode == "siteid":
					# Site ID search is exact match on the appropriate ID column
					where_sql = f"{siteid_col} = %s"
					params = [q_value]
				elif search_mode == "url":
					# URL search uses ILIKE
					where_sql = f"{url_col} ILIKE %s"
					params = [f"%{q_value}%"]
				else:
					# Company search uses ILIKE on the company column
					where_sql = f"{company_col} ILIKE %s"
					params = [f"%{q_value}%"]

				select_clause = "*"
				# Add HQ filter if requested
				if hq_only:
					if 2000 <= year <= 2015:
						where_sql += " AND corphdq = 'Ultimate HQ'"
					elif 2016 <= year <= 2020:
						table = f"usa_{year}_site_description t1 JOIN usa_{year}_site_level_enterprise t2 ON t1.siteid = t2.siteid"
						select_clause = "t1.*"
						if search_mode == "siteid":
							where_sql = where_sql.replace("siteid =", "t1.siteid =")
						where_sql += " AND t2.corphdq = 'Headquarter'"
					elif 2021 <= year <= 2022:
						where_sql += " AND site_type = 'Headquarters'"

				# Add Government Level filter if requested
				if gov_filter and gov_levels:
					gov_col = None
					if 2000 <= year <= 2020:
						gov_col = "govtlevel"
					elif 2021 <= year <= 2022:
						gov_col = "site_govt_level"
					
					if gov_col:
						gov_conditions = []
						for level in gov_levels:
							if level == "Enterprise":
								gov_conditions.append(f"({gov_col} IS NULL OR {gov_col} = '')")
							else:
								gov_conditions.append(f"{gov_col} ILIKE %s")
								params.append(level)
						
						if gov_conditions:
							where_sql += " AND (" + " OR ".join(gov_conditions) + ")"

				if where_sql:
					query = f"SELECT {select_clause} FROM {table} WHERE {where_sql} LIMIT 500;"
				else:
					query = None

				if query:
					try:
						conn = get_db_connection()
						with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
							cur.execute(query, params)
							rows = cur.fetchall()
							columns = [desc.name for desc in cur.description] if cur.description else []
					except Exception as exc:  # pragma: no cover
						error = str(exc)
					finally:
						try:
							conn.close()
						except Exception:
							pass

	return render_template(
		"companies.html",
		rows=rows,
		columns=columns,
		error=error,
		company_searched=company_searched,
		selected_year=selected_year,
		search_mode=search_mode,
		q_value=q_value,
		hq_only=hq_only,
		gov_filter=gov_filter,
		gov_levels=gov_levels,
	)


@app.route("/api/company-search")
def company_search_api():
	"""JSON API: search companies by name, site ID, or URL and year.

	Expected query parameters:
	- q: search value (required)
	- mode: 'company', 'siteid', or 'url' (default: 'company')
	- year: integer year between 2000 and 2022 (required)

	Returns JSON with keys:
	- columns: list of column names
	- rows: list of row objects (as dictionaries)
	- error: optional error message
	"""

	q_value = request.args.get("q", "").strip()
	# Fallback for backward compatibility
	if not q_value:
		q_value = request.args.get("company", "").strip()

	search_mode = request.args.get("mode", "company")
	year_raw = request.args.get("year")
	hq_only = request.args.get("hq_only") == "true" or request.args.get("hq_only") == "on"

	if not q_value or not year_raw:
		return jsonify({"error": "Both search value and year are required."}), 400

	rows = []
	columns = []
	try:
		year = int(year_raw)
	except (TypeError, ValueError):
		return jsonify({"error": "Year must be a valid number."}), 400

	# Choose table and column pattern based on year (same logic as /companies)
	if year in (2000, 2009):
		# 2000 & 2009: usa_[year]_hist[year]_sitedesc
		table = f"usa_{year}_hist{year}_sitedesc"
		company_col = "company"
		siteid_col = "siteid"
		url_col = "homepageurl"
	elif 2010 <= year <= 2015:
		# 2010-2015: usa_[year]_hist[year]_sitedesc
		table = f"usa_{year}_hist{year}_sitedesc"
		company_col = "company"
		siteid_col = "siteid"
		url_col = "homepageurl"
	elif 2016 <= year <= 2020:
		# 2016-2020: usa_[year]_site_description
		table = f"usa_{year}_site_description"
		company_col = "company"
		siteid_col = "siteid"
		url_col = "homepageurl"
	elif 2020 <= year <= 2022:
		# 2020-2022: usa_[year]_sites
		table = f"usa_{year}_sites"
		company_col = "site_name"
		siteid_col = "site_id"
		url_col = "site_url"
	else:
		return jsonify({"error": "Year must be between 2000 and 2022."}), 400

	# Decide which field to filter on based on search mode
	if search_mode == "siteid":
		# Site ID search is exact match on the appropriate ID column
		where_sql = f"{siteid_col} = %s"
		params = [q_value]
	elif search_mode == "url":
		# URL search uses ILIKE
		where_sql = f"{url_col} ILIKE %s"
		params = [f"%{q_value}%"]
	else:
		# Company search uses ILIKE on the company column
		where_sql = f"{company_col} ILIKE %s"
		params = [f"%{q_value}%"]

	select_clause = "*"
	# Add HQ filter if requested
	if hq_only:
		if 2000 <= year <= 2015:
			where_sql += " AND corphdq = 'Ultimate HQ'"
		elif 2016 <= year <= 2020:
			table = f"usa_{year}_site_description t1 JOIN usa_{year}_sitelevelenterprise t2 ON t1.siteid = t2.siteid"
			select_clause = "t1.*"
			if search_mode == "siteid":
				where_sql = where_sql.replace("siteid =", "t1.siteid =")
			where_sql += " AND t2.corphdq = 'Ultimate HQ'"
		elif 2021 <= year <= 2022:
			where_sql += " AND site_type = 'Headquarters'"

	query = f"SELECT {select_clause} FROM {table} WHERE {where_sql} LIMIT 500;"

	try:
		conn = get_db_connection()
		with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute(query, params)
			rows = cur.fetchall()
			columns = [desc.name for desc in cur.description] if cur.description else []
	except Exception as exc:  # pragma: no cover
		return jsonify({"error": str(exc)}), 500
	finally:
		try:
			conn.close()
		except Exception:
			pass

	return jsonify({"columns": columns, "rows": rows})


@app.route("/companies-accounts")
def companies_accounts():
	"""Companies Accounts search page.

	Search by company name and year across account-level tables.

	Year ranges and table/column mapping:
	- 2000 & 2009: usa_[year]_hist[year]_sitedesc.company
	- 2010-2015: usa_[year]_hist[year]_enterprise.ent_company
	- 2016-2020: usa_[year]_site_level_enterprise.ent_company
	- 2020-2022: usa_[year]_accounts.account_name
	"""

	company_name = request.args.get("company", "").strip()
	year_raw = request.args.get("year")

	rows = []
	columns = []
	error = None
	company_searched = bool(company_name)
	selected_year = None

	if company_name and year_raw:
		try:
			year = int(year_raw)
		except (TypeError, ValueError):
			error = "Year must be a valid number."
		else:
			selected_year = year
			# Choose table and column pattern based on year
			if year in (2000, 2009):
				# 2000 & 2009: usa_[year]_hist[year]_sitedesc, company column
				table = f"usa_{year}_hist{year}_sitedesc"
				company_col = "company"
			elif 2010 <= year <= 2015:
				# 2010-2015: usa_[year]_hist[year]_enterprise, ent_company column
				table = f"usa_{year}_hist{year}_enterprise"
				company_col = "ent_company"
			elif 2016 <= year <= 2020:
				# 2016-2020: usa_[year]_site_level_enterprise, ent_company column
				table = f"usa_{year}_site_level_enterprise"
				company_col = "ent_company"
			elif 2020 <= year <= 2022:
				# 2020-2022: usa_[year]_accounts, account_name column
				table = f"usa_{year}_accounts"
				company_col = "account_name"
			else:
				error = "Year must be between 2000 and 2022."

			if not error:
				where_sql = f"{company_col} ILIKE %s"
				params = [f"%{company_name}%"]
				query = f"SELECT * FROM {table} WHERE {where_sql} LIMIT 500;"

				try:
					conn = get_db_connection()
					with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
						cur.execute(query, params)
						rows = cur.fetchall()
						columns = [desc.name for desc in cur.description] if cur.description else []
				except Exception as exc:  # pragma: no cover
					error = str(exc)
				finally:
					try:
						conn.close()
					except Exception:
						pass

	return render_template(
		"companies_accounts.html",
		rows=rows,
		columns=columns,
		error=error,
		company_searched=company_searched,
		selected_year=selected_year,
	)


# ---------------------------------------------------------------------------
# SQL Explorer
# ---------------------------------------------------------------------------

QUERY_DEFAULT_LIMIT = 1000
QUERY_MAX_LIMIT = 10000
QUERY_TIMEOUT_MS = 120_000
# Statements that produce a result set without modifying anything.
QUERY_ALLOWED_PREFIXES = ("select", "with", "explain", "show", "table", "values")
_SQL_COMMENT_RE = re.compile(r"--[^\n]*|/\*.*?\*/", re.S)
# Types reported to the UI so numeric columns sort/align correctly.
_NUMERIC_PG_TYPES = {
	"int2", "int4", "int8", "float4", "float8", "numeric", "money", "oid",
}
_PG_TYPE_NAMES = {}
_PG_TYPE_LOCK = threading.Lock()


def _strip_sql(sql):
	"""Remove comments and the trailing semicolon so the statement can be inspected/wrapped."""
	cleaned = _SQL_COMMENT_RE.sub(" ", sql).strip()
	while cleaned.endswith(";"):
		cleaned = cleaned[:-1].rstrip()
	return cleaned


def _json_safe(value):
	"""Make a database value JSON serialisable (Decimal, dates, UUID, bytes, ...)."""
	if value is None or isinstance(value, (bool, int, float, str)):
		return value
	if isinstance(value, (list, tuple)):
		return [_json_safe(v) for v in value]
	if isinstance(value, dict):
		return {str(k): _json_safe(v) for k, v in value.items()}
	if isinstance(value, (bytes, memoryview)):
		return bytes(value).hex()
	return str(value)


def _pg_type_names(cur, oids):
	"""Resolve pg_type OIDs to names, caching results between requests."""
	missing = [o for o in set(oids) if o not in _PG_TYPE_NAMES]
	if missing:
		cur.execute("SELECT oid, typname FROM pg_type WHERE oid = ANY(%s)", (missing,))
		with _PG_TYPE_LOCK:
			for oid, name in cur.fetchall():
				_PG_TYPE_NAMES[oid] = name
	return [_PG_TYPE_NAMES.get(o, "unknown") for o in oids]


def _dedupe_columns(names):
	"""Give repeated column names (e.g. two `id` columns from a join) unique keys."""
	seen, out = {}, []
	for name in names:
		if name in seen:
			seen[name] += 1
			out.append(f"{name}_{seen[name]}")
		else:
			seen[name] = 1
			out.append(name)
	return out


@app.route("/api/query", methods=["POST"])
def run_query():
	"""Run an ad-hoc read-only SQL query and return rows, column metadata and timing.

	Guardrails: read-only transaction, statement timeout, single statement only,
	and a server-side cursor capped at ``limit`` rows (``truncated`` flags when
	more rows were available). Intended for trusted internal users.
	"""
	payload = request.json or {}
	sql = payload.get("sql")
	if not sql or not isinstance(sql, str) or not sql.strip():
		return jsonify({"error": "No SQL query provided."}), 400

	try:
		limit = int(payload.get("limit") or QUERY_DEFAULT_LIMIT)
	except (TypeError, ValueError):
		limit = QUERY_DEFAULT_LIMIT
	limit = max(1, min(limit, QUERY_MAX_LIMIT))

	statement = _strip_sql(sql)
	if not statement:
		return jsonify({"error": "No SQL query provided."}), 400
	first_word = statement.split(None, 1)[0].lower()
	if first_word not in QUERY_ALLOWED_PREFIXES:
		return jsonify({"error": "Only read-only statements are allowed (SELECT, WITH, EXPLAIN, SHOW, TABLE, VALUES)."}), 400
	if ";" in statement:
		return jsonify({"error": "Only a single statement can be run at a time."}), 400

	conn = None
	use_named = False
	cursor_name = ""
	started = datetime.now()
	try:
		conn = get_db_connection()
		conn.set_session(readonly=True, autocommit=False)
		with conn:
			with conn.cursor() as setup:
				setup.execute("SET statement_timeout = %s", (QUERY_TIMEOUT_MS,))
			# EXPLAIN/SHOW cannot be wrapped in a server-side cursor; they are tiny anyway.
			use_named = first_word in ("select", "with", "table", "values")
			cursor_name = "swdb_explorer"
			cur = conn.cursor(name=cursor_name if use_named else None)
			with cur:
				if use_named:
					cur.itersize = min(limit + 1, 2000)
				cur.execute(statement)
				raw_rows = cur.fetchmany(limit + 1)
				description = cur.description or []
				truncated = len(raw_rows) > limit
				raw_rows = raw_rows[:limit]
				with conn.cursor() as meta:
					type_names = _pg_type_names(meta, [d.type_code for d in description])
	except psycopg2.Error as exc:
		diag = exc.diag
		position = int(diag.statement_position) if diag.statement_position else None
		if position and use_named:
			# psycopg2 wraps named-cursor queries in DECLARE ... FOR <sql>; undo that offset.
			position -= len(f'DECLARE "{cursor_name}" CURSOR WITHOUT HOLD FOR ')
			position = position if position > 0 else None
		snippet, snippet_start = None, 0
		if position:
			snippet_start = max(0, position - 31)
			snippet = statement[snippet_start:min(len(statement), position + 29)]
		detail = {
			"error": (diag.message_primary or str(exc)).strip(),
			"detail": diag.message_detail,
			"hint": diag.message_hint,
			"position": position,
			"snippet": snippet,
			"snippet_start": snippet_start,
			"code": diag.sqlstate,
		}
		if diag.sqlstate == "57014":
			detail["error"] = f"Query cancelled: exceeded the {QUERY_TIMEOUT_MS // 1000}s time limit."
		return jsonify(detail), 400
	except Exception as exc:  # pragma: no cover - simple error surface
		return jsonify({"error": str(exc)}), 400
	finally:
		if conn is not None:
			try:
				conn.close()
			except Exception:
				pass

	names = _dedupe_columns([d.name for d in description])
	columns = [
		{"field": name, "type": tname, "numeric": tname in _NUMERIC_PG_TYPES}
		for name, tname in zip(names, type_names)
	]
	rows = [dict(zip(names, (_json_safe(v) for v in row))) for row in raw_rows]
	elapsed_ms = int((datetime.now() - started).total_seconds() * 1000)

	return jsonify({
		"columns": columns,
		"rows": rows,
		"row_count": len(rows),
		"truncated": truncated,
		"limit": limit,
		"elapsed_ms": elapsed_ms,
	})


@app.route("/technologies")
def technologies():
	"""Technologies view for a given site and year.

	Expects query parameters:
	- siteid: clicked site id from companies table
	- year: year used on the companies page

	Year ranges and table/column mapping:
	- 2000 & 2009: usa_[year]_hist[year]_sitedesc where siteid = [siteid]
	- 2010-2015: usa_[year]_hist[year]_model where siteid = [siteid]
	- 2016-2020: usa_[year]_productinstall where siteid = [siteid]
	- 2020-2022: usa_[year]_technologies where site_id = [siteid]
	"""

	siteid = request.args.get("siteid")
	year_raw = request.args.get("year")

	rows = []
	columns = []
	error = None
	selected_year = None

	if siteid and year_raw:
		try:
			year = int(year_raw)
		except (TypeError, ValueError):
			error = "Year must be a valid number."
		else:
			selected_year = year
			# Choose table and id column based on year
			if year in (2000, 2009):
				# 2000 & 2009: usa_[year]_hist[year]_sitedesc, siteid column
				table = f"usa_{year}_hist{year}_sitedesc"
				id_col = "siteid"
			elif 2010 <= year <= 2015:
				# 2010-2015: usa_[year]_hist[year]_model, siteid column
				table = f"usa_{year}_hist{year}_model"
				id_col = "siteid"
			elif 2016 <= year <= 2020:
				# 2016-2020: usa_[year]_productinstall, siteid column
				table = f"usa_{year}_product_install"
				id_col = "siteid"
			elif 2020 <= year <= 2022:
				# 2020-2022: usa_[year]_sites_technology, site_id column
				table = f"usa_{year}_sites_technology"
				id_col = "site_id"
			else:
				error = "Year must be between 2000 and 2022."

			if not error:
				where_sql = f"{id_col} = %s"
				params = [siteid]
				query = f"SELECT * FROM {table} WHERE {where_sql} LIMIT 500;"

				try:
					conn = get_db_connection()
					with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
						cur.execute(query, params)
						rows = cur.fetchall()
						columns = [desc.name for desc in cur.description] if cur.description else []
				except Exception as exc:  # pragma: no cover
					error = str(exc)
				finally:
					try:
						conn.close()
					except Exception:
						pass

	return render_template(
		"technologies.html",
		rows=rows,
		columns=columns,
		error=error,
		selected_year=selected_year,
		siteid=siteid,
	)


@app.route("/compare-technologies")
def compare_technologies():
	"""Compare technologies between two sites (optionally different years)."""

	siteid = request.args.get("siteid")
	year_raw = request.args.get("year")
	comp_siteid = request.args.get("siteid2")
	comp_year_raw = request.args.get("year2")

	rows = []
	columns = []
	selected_year = None
	comp_rows = []
	comp_columns = []
	comp_selected_year = None
	error = None

	def build_query(year: int, siteid_value: str):
		"""Return parametrized SQL and params for a given year bucket.

		This adds the appropriate JOIN on the description/lookup tables and
		filters by siteid / site_id as requested.
		"""

		if year in (2000, 2009):
			# 2000 & 2009: usa_2009_hist2009_model + usa_2009_hist2009_modeldesc
			# Example:
			# SELECT *
			# FROM usa_2009_hist2009_model pi
			# JOIN usa_2009_hist2009_modeldesc ps
			#   ON pi.tabkey = ps.tabkey
			# WHERE pi.siteid = '137000393';
			query = (
				"SELECT * "
				"FROM usa_2009_hist2009_model pi "
				"JOIN usa_2009_hist2009_modeldesc ps "
				"ON pi.tabkey = ps.tabkey "
				"WHERE pi.siteid = %s "
				"LIMIT 500;"
			)
			params = [siteid_value]
		elif 2010 <= year <= 2015:
			# 2010-2015: same pair as above per user example
			query = (
				"SELECT * "
				"FROM usa_2009_hist2009_model pi "
				"JOIN usa_2009_hist2009_modeldesc ps "
				"ON pi.tabkey = ps.tabkey "
				"WHERE pi.siteid = %s "
				"LIMIT 500;"
			)
			params = [siteid_value]
		elif 2016 <= year <= 2020:
			# 2016-2020: usa_2018_product_install + usa_2018_product_specifications
			query = (
				"SELECT * "
				"FROM usa_2018_product_install pi "
				"JOIN usa_2018_product_specifications ps "
				"ON pi.tabkey = ps.tabkey "
				"WHERE pi.siteid = %s "
				"LIMIT 500;"
			)
			params = [siteid_value]
		elif 2021 <= year <= 2022:
			# 2021-2022: usa_2022_sites_technology + usa_2022_technology_lookup
			query = (
				"SELECT * "
				"FROM usa_2022_sites_technology pi "
				"JOIN usa_2022_technology_lookup ps "
				"ON pi.product_id = ps.product_id "
				"WHERE pi.site_id = %s "
				"LIMIT 500;"
			)
			params = [siteid_value]
		else:
			return None, None

		return query, params

	# Base query
	if siteid and year_raw:
		try:
			year = int(year_raw)
		except (TypeError, ValueError):
			error = "Base year must be a valid number."
		else:
			selected_year = year
			query, params = build_query(year, siteid)
			if not query:
				error = "Base year must be within supported ranges (2000-2009, 2010-2015, 2016-2020, 2021-2022)."
			else:
				try:
					conn = get_db_connection()
					with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
						cur.execute(query, params)
						rows = cur.fetchall()
						columns = [desc.name for desc in cur.description] if cur.description else []
				except Exception as exc:  # pragma: no cover
					error = str(exc)
				finally:
					try:
						conn.close()
					except Exception:
						pass

	# Comparison query
	if not error and comp_siteid and comp_year_raw:
		try:
			comp_year = int(comp_year_raw)
		except (TypeError, ValueError):
			error = "Comparison year must be a valid number."
		else:
			comp_selected_year = comp_year
			query, params = build_query(comp_year, comp_siteid)
			if not query:
				error = "Comparison year must be within supported ranges (2000-2009, 2010-2015, 2016-2020, 2021-2022)."
			else:
				try:
					conn = get_db_connection()
					with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
						cur.execute(query, params)
						comp_rows = cur.fetchall()
						comp_columns = [desc.name for desc in cur.description] if cur.description else []
				except Exception as exc:  # pragma: no cover
					error = str(exc)
				finally:
					try:
						conn.close()
					except Exception:
						pass

	return render_template(
		"compare_technologies.html",
		rows=rows,
		columns=columns,
		comp_rows=comp_rows,
		comp_columns=comp_columns,
		error=error,
		selected_year=selected_year,
		comp_selected_year=comp_selected_year,
		siteid=siteid,
		comp_siteid=comp_siteid,
	)


@app.route("/swdb-structure")
def swdb_structure():
	"""Render the SWDB structure markdown file as an HTML page."""

	md_path = Path(__file__).with_name("swdb_structure.md")
	markdown_html = ""
	try:
		markdown_text = md_path.read_text(encoding="utf-8")
		markdown_html = markdown.markdown(markdown_text, extensions=["fenced_code", "tables"])
	except FileNotFoundError:
		markdown_html = "<p><strong>swdb_structure.md</strong> file not found.</p>"
	except Exception as exc:  # pragma: no cover
		markdown_html = f"<p>Error loading markdown: {exc}</p>"

	return render_template("swdb_structure.html", content=markdown_html)


@app.route("/swdb-schema")
def swdb_schema():
	"""Render the RDF v4.1 (2020-2022) SWDB schema page."""
	return render_template("swdb_schema.html", schema_versions=_schema_versions("v4.1"))


def _schema_versions(current):
	"""All SWDB schema versions (RDF v4.1 + CCID dictionaries) for the in-page version switcher."""
	versions = [{
		"key": "v4.1", "short": "v4.1 · 2020-22", "title": "RDF v4.1 (2020-2022)",
		"url": url_for("swdb_schema"), "available": True,
	}]
	for k, v in CCID_VERSIONS.items():
		versions.append({
			"key": k, "short": v["short"], "title": v["title"],
			"url": url_for("ccid_schema", key=k), "available": v["path"].is_file(),
		})
	for v in versions:
		v["current"] = v["key"] == current
	return versions


# ---------------------------------------------------------------------------
# CCID schemas (2023+) — ER diagrams built from the RDF data dictionary xlsx files
# ---------------------------------------------------------------------------

_DOCS = Path(__file__).parent / "data" / "documentation"
# Ordered oldest → newest; each version is diffed against the previous entry.
CCID_VERSIONS = {
	"2023": {"title": "CCID v5.0 (2023)", "short": "v5.0 · 2023",
			 "path": _DOCS / "2023" / "RDF_v5.0_for_2023_CCID.xlsx"},
	"2024": {"title": "CCID v5.1 (2024)", "short": "v5.1 · 2024",
			 "path": _DOCS / "2024" / "RDF_v5.1_for_2024_CCID_data.xlsx"},
	"2025": {"title": "C&C v5.2 (2025)", "short": "v5.2 · 2025",
			 "path": _DOCS / "2025" / "RDF_v5.2_for_2025_C&C_data.xlsx"},
}
CCID_DEFAULT_VERSION = list(CCID_VERSIONS)[-1]
CCID_REL_COLORS = {"data": "#2563eb", "lookup": "#16a34a", "fk": "#7c3aed"}
CCID_POSITIONS = {
	"COMPANY_TECH_SIZING": {"x": 20, "y": 60},
	"COMPANY_TECHNOLOGY": {"x": 20, "y": 660},
	"TECHNOLOGY_LOOKUP": {"x": 20, "y": 1010},
	"COMPANY": {"x": 500, "y": 60},
	"SITE": {"x": 1000, "y": 60},
	"SITE_TECH_SIZING": {"x": 1500, "y": 60},
}
_ccid_schema_cache = {}


def _ccid_field_type(field_type, length):
	"""Compact type label shown next to each field, e.g. Text(128), Numeric, Array(512)."""
	ftype = (field_type or "").strip() or "?"
	length = (length or "").strip()
	return f"{ftype}({length})" if length else ftype


def _ccid_previous_version(key):
	keys = list(CCID_VERSIONS)
	idx = keys.index(key)
	return keys[idx - 1] if idx > 0 else None


def _load_ccid_schema(key):
	"""Parse one CCID data dictionary workbook into the structures the ER diagram expects."""
	version = CCID_VERSIONS[key]
	xlsx = version["path"]
	mtime = xlsx.stat().st_mtime
	cached = _ccid_schema_cache.get(key)
	if cached and cached["mtime"] == mtime:
		return cached

	book = pd.read_excel(xlsx, sheet_name=None, dtype=str, keep_default_na=False)
	dd = book["Data Dictionary"]
	dd = dd.apply(lambda s: s.str.strip())

	# Table descriptions live in the "Tables" sheet (header row is the first data row).
	descriptions = {}
	tables_sheet = book.get("Tables")
	if tables_sheet is not None and not tables_sheet.empty:
		tbl = tables_sheet.iloc[1:].copy()
		tbl.columns = [str(c).strip() for c in tables_sheet.iloc[0]]
		if "Table name" in tbl.columns and "Description" in tbl.columns:
			for _, row in tbl.iterrows():
				name = str(row["Table name"]).strip()
				if name:
					descriptions[name.upper()] = str(row["Description"]).strip()

	# Canonical table names are upper-case; keep the first spelling seen for display.
	canonical = {}
	for name in dd["Table name"]:
		canonical.setdefault(name.upper(), name.upper())

	fk_re = re.compile(r"FK\s+to\s+\[([^\]]+)\]\.\[([^\]]+)\]", re.IGNORECASE)

	schema, field_defs, pk_owner = {}, {}, {}
	fk_links = []
	for _, row in dd.sort_values(["Table ID", "Field order"], key=lambda s: s.map(_ccid_sort_key)).iterrows():
		table = canonical[row["Table name"].upper()]
		field = row["Field name"]
		if table not in schema:
			schema[table] = {
				"type": row["Table type"].lower() or "data",
				"desc": descriptions.get(table, ""),
				"fields": [],
			}

		key_kind = ""
		fk_target = None
		raw_key = row["Key"]
		if raw_key.upper() == "PK":
			key_kind = "PK"
			pk_owner.setdefault(field, table)
		elif raw_key.upper() == "CPK":
			key_kind = "CPK"
			pk_owner.setdefault(field, table)
		elif fk_re.search(raw_key):
			key_kind = "FK"
			ref_table, ref_field = fk_re.search(raw_key).groups()
			ref_table = canonical.get(ref_table.upper(), ref_table.upper())
			fk_target = f"{ref_table}.{ref_field}"
			fk_links.append((ref_table, table))

		schema[table]["fields"].append({
			"name": field,
			"type": _ccid_field_type(row["Field type"], row["Field length"]),
			**({"key": key_kind} if key_kind else {}),
		})

		info = {"def": row["Definition"], "topic": row["Topic"]}
		if row["Possible values"]:
			info["values"] = [v.strip() for v in row["Possible values"].split("|") if v.strip()]
		if fk_target:
			info["fk"] = fk_target
		if row["Applies to"]:
			info["applies"] = row["Applies to"]
		if row["Format"]:
			info["format"] = row["Format"]
		if row["Default value"]:
			info["default"] = row["Default value"]
		field_defs[f"{table}.{field}"] = info

	relationships, seen = [], set()
	for parent, child in fk_links:
		if (parent, child) in seen or parent not in schema:
			continue
		seen.add((parent, child))
		is_lookup = schema[parent]["type"] == "lookup"
		relationships.append({
			"from": parent, "to": child,
			"label": "1:N",
			"color": CCID_REL_COLORS["lookup" if is_lookup else "data"],
		})
	# Tables whose PK is the PK of another table (e.g. *_TECH_SIZING) are 1:1 extensions.
	for table, data in schema.items():
		for f in data["fields"]:
			if f.get("key") != "PK":
				continue
			owner = pk_owner.get(f["name"])
			if owner and owner != table and (owner, table) not in seen:
				seen.add((owner, table))
				relationships.append({"from": owner, "to": table, "label": "1:1", "color": CCID_REL_COLORS["fk"]})
				field_defs[f"{table}.{f['name']}"].setdefault("fk", f"{owner}.{f['name']}")

	# Diff against the previous version: new fields are flagged in the popup and the export.
	changes = {"previous": None, "added": [], "removed": []}
	prev_key = _ccid_previous_version(key)
	if prev_key and CCID_VERSIONS[prev_key]["path"].is_file():
		prev = _load_ccid_schema(prev_key)
		changes["previous"] = CCID_VERSIONS[prev_key]["title"]
		for fq, info in field_defs.items():
			if fq not in prev["field_defs"]:
				info["added_in"] = version["title"]
				table, field = fq.split(".", 1)
				changes["added"].append({"table": table, "field": field, "def": info["def"]})
		for fq, info in prev["field_defs"].items():
			if fq not in field_defs:
				table, field = fq.split(".", 1)
				changes["removed"].append({"table": table, "field": field, "def": info["def"]})

	result = {
		"mtime": mtime,
		"key": key,
		"title": version["title"],
		"source_name": xlsx.name,
		"schema": schema,
		"field_defs": field_defs,
		"relationships": relationships,
		"positions": {k: v for k, v in CCID_POSITIONS.items() if k in schema},
		"relevant_topics": sorted({d["topic"] for d in field_defs.values()
			if d["topic"] and ("Identification" in d["topic"] or "Sizing" in d["topic"] or "Industry" in d["topic"])}),
		"field_count": len(field_defs),
		"table_count": len(schema),
		"changes": changes,
	}
	_ccid_schema_cache[key] = result
	return result


def _ccid_sort_key(value):
	"""Sort '1.1', '1.2', '10' and plain integers numerically."""
	try:
		return tuple(int(p) for p in str(value).split("."))
	except ValueError:
		return (float("inf"),)


def _ccid_schema_or_404(key):
	if key not in CCID_VERSIONS:
		abort(404, description=f"Unknown CCID schema version '{key}'.")
	try:
		return _load_ccid_schema(key)
	except FileNotFoundError:
		abort(404, description=f"{CCID_VERSIONS[key]['path'].name} not found.")


@app.route("/ccid-schema")
def ccid_schema_default():
	"""Bare URL opens the newest data dictionary version."""
	return redirect(url_for("ccid_schema", key=CCID_DEFAULT_VERSION))


@app.route("/ccid-schema/<key>")
def ccid_schema(key):
	"""Render a CCID ER diagram from the matching RDF data dictionary workbook."""
	data = _ccid_schema_or_404(key)
	return render_template("ccid_schema.html", schema_versions=_schema_versions(key), **data)


def _ccid_schema_markdown(data):
	"""Serialize the parsed CCID schema as LLM-friendly Markdown (overview, relationships, tables)."""
	title = data["title"]
	schema, defs, rels = data["schema"], data["field_defs"], data["relationships"]
	esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ").strip()

	lines = [
		f"# {title} — Relational Data Format (RDF) Schema",
		"",
		f"Source: `{data['source_name']}` (Spiceworks Ziff-Davis data dictionary).",
		f"{data['table_count']} tables, {data['field_count']} fields. "
		"Table names and field names are used verbatim as SQL identifiers.",
		"",
		"Conventions: `PK` = primary key, `FK` = foreign key, `CPK` = composite primary key. "
		"Field types are `Text(max_length)`, `Numeric`, `Array(max_length)` (pipe/comma separated list stored as text), `Date`. "
		"`Default` is the value stored when no data is available (`NULL` means missing).",
		"",
		"## Tables overview",
		"",
		"| Table | Type | Fields | Description |",
		"|---|---|---|---|",
	]
	for name, t in schema.items():
		lines.append(f"| `{name}` | {t['type']} | {len(t['fields'])} | {esc(t.get('desc', ''))} |")

	lines += ["", "## Relationships", ""]
	for r in rels:
		child_fk = next(
			(f["name"] for f in schema[r["to"]]["fields"]
			 if defs.get(f"{r['to']}.{f['name']}", {}).get("fk", "").startswith(r["from"] + ".")),
			None,
		)
		parent_key = defs.get(f"{r['to']}.{child_fk}", {}).get("fk", "") if child_fk else ""
		join = f"`{r['to']}.{child_fk}` = `{parent_key}`" if child_fk else ""
		lines.append(f"- `{r['from']}` → `{r['to']}` ({r['label']}){': ' + join if join else ''}")
	lines += [
		"",
		"Typical joins: `COMPANY` is the root entity; `SITE` rows belong to a company via `COMPANY_ID`; "
		"`COMPANY_TECHNOLOGY` lists installed technologies per company and resolves to `TECHNOLOGY_LOOKUP` via `TECH_ID`; "
		"`*_TECH_SIZING` tables extend their parent 1:1 on the same primary key.",
	]

	changes = data.get("changes") or {}
	if changes.get("previous"):
		lines += ["", f"## Changes vs. {changes['previous']}", ""]
		if not changes["added"] and not changes["removed"]:
			lines.append("- No field additions or removals; the schema is unchanged.")
		for c in changes["added"]:
			lines.append(f"- Added `{c['table']}.{c['field']}` — {esc(c['def'])}")
		for c in changes["removed"]:
			lines.append(f"- Removed `{c['table']}.{c['field']}` — {esc(c['def'])}")

	for name, t in schema.items():
		lines += [
			"",
			f"## Table `{name}` ({t['type']}, {len(t['fields'])} fields)",
			"",
		]
		if t.get("desc"):
			lines += [esc(t["desc"]), ""]
		lines += [
			"| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |",
			"|---|---|---|---|---|---|---|---|---|",
		]
		for i, f in enumerate(t["fields"], 1):
			d = defs.get(f"{name}.{f['name']}", {})
			key = f.get("key", "")
			if d.get("fk"):
				key = f"{key or 'FK'} → `{d['fk']}`"
			notes = []
			if d.get("applies"):
				notes.append(f"Applies to: {d['applies']}")
			if d.get("format"):
				notes.append(f"Format: {d['format']}")
			if d.get("added_in"):
				notes.append(f"New in {d['added_in']}")
			lines.append(
				f"| {i} | `{f['name']}` | {f['type']} | {esc(key)} | {esc(d.get('def', ''))} | "
				f"{esc(d.get('topic', ''))} | {esc(' / '.join(d.get('values', [])))} | "
				f"{esc(d.get('default', ''))} | {esc('; '.join(notes))} |"
			)
	return "\n".join(lines) + "\n"


@app.route("/ccid-schema/<key>/export.md")
def ccid_schema_export(key):
	"""Download a CCID schema as Markdown optimised for LLM consumption."""
	data = _ccid_schema_or_404(key)
	md = _ccid_schema_markdown(data)
	filename = re.sub(r"[^A-Za-z0-9]+", "_", data["title"]).strip("_").lower() + "_schema_llm.md"
	return Response(
		md,
		mimetype="text/markdown",
		headers={"Content-Disposition": f"attachment; filename={filename}"},
	)


# ---------------------------------------------------------------------------
# Documentation (RDF manuals + data dictionaries) viewer
# ---------------------------------------------------------------------------

DOCUMENTATION_DIR = Path(__file__).parent / "data" / "documentation"
DOCUMENTATION_EXTENSIONS = {".pdf": "pdf", ".xlsx": "xlsx", ".xls": "xlsx"}


def _list_documentation_files():
	"""Return the viewable files under data/documentation, grouped by folder."""
	groups = {}
	if not DOCUMENTATION_DIR.is_dir():
		return []
	for path in sorted(DOCUMENTATION_DIR.rglob("*")):
		kind = DOCUMENTATION_EXTENSIONS.get(path.suffix.lower())
		if not path.is_file() or kind is None or path.name.startswith("."):
			continue
		rel = path.relative_to(DOCUMENTATION_DIR)
		folder = str(rel.parent) if str(rel.parent) != "." else ""
		groups.setdefault(folder, []).append(
			{"name": path.name, "rel": rel.as_posix(), "kind": kind,
			 "size_kb": round(path.stat().st_size / 1024)}
		)
	return [{"folder": k, "files": v} for k, v in groups.items()]


def _resolve_documentation_file(rel):
	"""Resolve a relative documentation path, refusing anything outside the folder."""
	if not rel:
		return None
	base = DOCUMENTATION_DIR.resolve()
	target = (base / rel).resolve()
	if base not in target.parents or not target.is_file():
		return None
	if target.suffix.lower() not in DOCUMENTATION_EXTENSIONS:
		return None
	return target


@app.route("/documentation")
def documentation():
	"""Browse the RDF documentation: PDFs inline, Excel sheets via Tabulator."""
	selected_rel = request.args.get("file", "")
	selected = _resolve_documentation_file(selected_rel)
	context = {
		"groups": _list_documentation_files(),
		"selected": None,
		"sheets": None,
		"error": None,
	}
	if selected_rel and selected is None:
		context["error"] = "File not found."
	if selected is not None:
		kind = DOCUMENTATION_EXTENSIONS[selected.suffix.lower()]
		context["selected"] = {
			"name": selected.name,
			"rel": selected.relative_to(DOCUMENTATION_DIR).as_posix(),
			"kind": kind,
		}
		if kind == "xlsx":
			try:
				frames = pd.read_excel(selected, sheet_name=None, dtype=str, keep_default_na=False)
				sheets = []
				for sheet_name, df in frames.items():
					df.columns = [str(c) for c in df.columns]
					non_empty = df.apply(lambda s: s.astype(str).str.strip().ne("").any())
					df = df.loc[:, non_empty]
					sheets.append({
						"name": str(sheet_name),
						"columns": list(df.columns),
						"rows": df.to_dict(orient="records"),
					})
				context["sheets"] = sheets
			except Exception as exc:  # pragma: no cover
				context["error"] = f"Could not read workbook: {exc}"
	return render_template("documentation.html", **context)


@app.route("/documentation/file/<path:rel>")
def documentation_file(rel):
	"""Serve a documentation file inline so the browser can display it."""
	if _resolve_documentation_file(rel) is None:
		abort(404)
	return send_from_directory(DOCUMENTATION_DIR, rel, as_attachment=False)


@app.route("/technology-history")
def technology_history():
	"""Technology History page."""
	return render_template("technology_history.html")


@app.route("/api/technology-history")
def technology_history_api():
	"""JSON API: Get technology history for a site over a range of years."""
	siteid = request.args.get("siteid")
	start_year_raw = request.args.get("start_year")
	end_year_raw = request.args.get("end_year")

	if not siteid or not start_year_raw or not end_year_raw:
		return jsonify({"error": "Missing required parameters."}), 400

	try:
		start_year = int(start_year_raw)
		end_year = int(end_year_raw)
	except ValueError:
		return jsonify({"error": "Years must be valid numbers."}), 400

	if start_year > end_year:
		return jsonify({"error": "Start year must be less than or equal to end year."}), 400

	if not (2000 <= start_year <= 2022) or not (2000 <= end_year <= 2022):
		return jsonify({"error": "Years must be between 2000 and 2022."}), 400

	results = {}
	site_name = None

	conn = None
	try:
		conn = get_db_connection()
		
		# Attempt to fetch site name from the most recent year in range
		for year in range(end_year, start_year - 1, -1):
			name_query = None
			if 2021 <= year <= 2022:
				name_query = f"SELECT site_name FROM usa_{year}_sites WHERE site_id = %s LIMIT 1;"
			elif 2016 <= year <= 2020:
				name_query = f"SELECT company FROM usa_{year}_site_description WHERE siteid = %s LIMIT 1;"
			elif 2000 <= year <= 2015:
				name_query = f"SELECT company FROM usa_{year}_hist{year}_sitedesc WHERE siteid = %s LIMIT 1;"
			
			if name_query:
				try:
					with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
						cur.execute(name_query, [siteid])
						row = cur.fetchone()
						if row:
							site_name = row.get('site_name') or row.get('company')
							break
				except Exception:
					conn.rollback()
					continue

		# We will reuse the connection for multiple queries

		for year in range(start_year, end_year + 1):
			query = None
			params = []

			# Logic adapted from compare_technologies but using dynamic year
			if year in (2000, 2009):
				# 2000 & 2009: usa_{year}_hist{year}_model + usa_{year}_hist{year}_modeldesc
				query = (
					f"SELECT * "
					f"FROM usa_{year}_hist{year}_model pi "
					f"JOIN usa_{year}_hist{year}_modeldesc ps "
					f"ON pi.tabkey = ps.tabkey "
					f"WHERE pi.siteid = %s "
					f"LIMIT 500;"
				)
				params = [siteid]
			elif 2010 <= year <= 2015:
				# 2010-2015: usa_{year}_hist{year}_model + usa_{year}_hist{year}_modeldesc
				query = (
					f"SELECT * "
					f"FROM usa_{year}_hist{year}_model pi "
					f"JOIN usa_{year}_hist{year}_modeldesc ps "
					f"ON pi.tabkey = ps.tabkey "
					f"WHERE pi.siteid = %s "
					f"LIMIT 500;"
				)
				params = [siteid]
			elif 2016 <= year <= 2020:
				# 2016-2020: usa_{year}_product_install + usa_{year}_product_specifications
				query = (
					f"SELECT * "
					f"FROM usa_{year}_product_install pi "
					f"JOIN usa_{year}_product_specifications ps "
					f"ON pi.tabkey = ps.tabkey "
					f"WHERE pi.siteid = %s "
					f"LIMIT 500;"
				)
				params = [siteid]
			elif 2021 <= year <= 2022:
				# 2021-2022: usa_{year}_sites_technology + usa_{year}_technology_lookup
				query = (
					f"SELECT * "
					f"FROM usa_{year}_sites_technology pi "
					f"JOIN usa_{year}_technology_lookup ps "
					f"ON pi.product_id = ps.product_id "
					f"WHERE pi.site_id = %s "
					f"LIMIT 500;"
				)
				params = [siteid]

			if query:
				try:
					with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
						cur.execute(query, params)
						rows = cur.fetchall()

						# Deduplicate columns
						all_cols = [desc.name for desc in cur.description] if cur.description else []
						unique_cols = []
						seen_cols = set()
						for col in all_cols:
							if col not in seen_cols:
								unique_cols.append(col)
								seen_cols.add(col)

						# Filter out empty columns
						final_cols = []
						if rows:
							for col in unique_cols:
								has_data = False
								for row in rows:
									val = row.get(col)
									if val is not None and str(val).strip() != "":
										has_data = True
										break
								if has_data:
									final_cols.append(col)
						else:
							final_cols = unique_cols

						results[year] = {"rows": rows, "columns": final_cols}
				except Exception as e:
					# If table doesn't exist or other error, just return empty for that year or error message
					print(f"Error querying year {year}: {e}")
					results[year] = {"rows": [], "columns": [], "error": str(e)}
					conn.rollback()
			else:
				results[year] = {"rows": [], "columns": []}

	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			conn.close()

	return jsonify({"results": results, "site_name": site_name})


@app.route("/account-technologies")
def account_technologies():
	"""Account Technologies page.

	Lets the user enter a site_url. The page finds all sites matching that
	URL, picks the site with the largest number of employees, fetches its
	account_id, then lists every site belonging to that account along with
	the products installed at each site. It also computes the intersection
	of products across all sites and a pairwise Jaccard similarity matrix.

	Supported years: 2021, 2022 (these years use the new schema with
	site_url, account_id and product lookup tables).
	"""
	return render_template("account_technologies.html")


@app.route("/api/account-technologies/sites")
def account_technologies_sites_api():
	"""Step 1 endpoint: list all sites whose site_url matches.

	Returns every column from `usa_{year}_sites`, plus a suggested
	`top_site_id` (the matched site with the highest employee count) so
	the UI can highlight it as the default selection.
	"""
	site_url = request.args.get("site_url", "").strip()
	year_raw = request.args.get("year", "2022").strip()

	if not site_url:
		return jsonify({"error": "site_url is required."}), 400
	try:
		year = int(year_raw)
	except (TypeError, ValueError):
		return jsonify({"error": "Year must be a valid number."}), 400
	if year not in (2021, 2022):
		return jsonify({"error": "Only years 2021 and 2022 are supported."}), 400

	sites_table = f"usa_{year}_sites"
	accounts_table = f"usa_{year}_accounts"
	emp_num_sql = "COALESCE(NULLIF(site_employees, '')::bigint, 0)"
	acc_emp_num_sql = "COALESCE(NULLIF(account_employees, '')::bigint, 0)"

	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			# Exact case-insensitive match by default. Special-case: ada.org
			# also accepts variants like "ada.org/en".
			if site_url.lower().rstrip("/") == "ada.org":
				site_where = "LOWER(site_url) = %s OR LOWER(site_url) LIKE %s"
				site_params = ["ada.org", "ada.org/%"]
				acc_where = "LOWER(account_url) = %s OR LOWER(account_url) LIKE %s"
				acc_params = ["ada.org", "ada.org/%"]
			else:
				site_where = "LOWER(site_url) = LOWER(%s)"
				site_params = [site_url]
				acc_where = "LOWER(account_url) = LOWER(%s)"
				acc_params = [site_url]
			cur.execute(
				f"SELECT * FROM {sites_table} "
				f"WHERE {site_where} "
				f"ORDER BY {emp_num_sql} DESC LIMIT 500;",
				site_params,
			)
			rows = cur.fetchall()
			columns = [d.name for d in cur.description] if cur.description else []

			cur.execute(
				f"SELECT * FROM {accounts_table} "
				f"WHERE {acc_where} "
				f"ORDER BY {acc_emp_num_sql} DESC LIMIT 500;",
				acc_params,
			)
			account_rows = cur.fetchall()
			account_columns = [d.name for d in cur.description] if cur.description else []
	except Exception as exc:  # pragma: no cover
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			try:
				conn.close()
			except Exception:
				pass

	if not rows and not account_rows:
		return jsonify({"error": f"No sites or accounts match '{site_url}' in {year}."}), 404

	def _revenue(r):
		v = r.get("site_revenue_usd")
		try:
			return float(v) if v not in (None, "") else 0.0
		except (TypeError, ValueError):
			return 0.0

	def _type_rank(r):
		# Prefer UH, then HQ, then anything else.
		t = (r.get("site_type") or "").strip().upper()
		if t == "UH":
			return 0
		if t == "HQ":
			return 1
		return 2

	# Pick the default highlighted site: prefer site_type=UH, then HQ,
	# tie-break by highest site_revenue_usd.
	top = min(rows, key=lambda r: (_type_rank(r), -_revenue(r))) if rows else None
	return jsonify({
		"year": year,
		"site_url": site_url,
		"columns": columns,
		"rows": rows,
		"top_site_id": (top or {}).get("site_id"),
		"account_columns": account_columns,
		"accounts": account_rows,
	})


@app.route("/api/account-technologies/account")
def account_technologies_account_api():
	"""Step 2 endpoint: given a site_id, return the account row, all sibling
	sites, products per site, common products, and pairwise Jaccard similarity.
	"""
	site_id = request.args.get("site_id", "").strip()
	year_raw = request.args.get("year", "2022").strip()

	if not site_id:
		return jsonify({"error": "site_id is required."}), 400
	try:
		year = int(year_raw)
	except (TypeError, ValueError):
		return jsonify({"error": "Year must be a valid number."}), 400
	if year not in (2021, 2022):
		return jsonify({"error": "Only years 2021 and 2022 are supported."}), 400

	sites_table = f"usa_{year}_sites"
	accounts_table = f"usa_{year}_accounts"
	tech_table = f"usa_{year}_sites_technology"
	lookup_table = f"usa_{year}_technology_lookup"
	emp_num_sql = "COALESCE(NULLIF(site_employees, '')::bigint, 0)"

	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			# Resolve account_id from the chosen site
			cur.execute(
				f"SELECT account_id FROM {sites_table} WHERE site_id = %s LIMIT 1;",
				[site_id],
			)
			row = cur.fetchone()
			if not row or not row.get("account_id"):
				return jsonify({"error": f"site_id {site_id} not found or has no account_id."}), 404
			account_id = row["account_id"]

			# Account row (all columns)
			cur.execute(
				f"SELECT * FROM {accounts_table} WHERE account_id = %s LIMIT 1;",
				[account_id],
			)
			account = cur.fetchone()
			account_columns = [d.name for d in cur.description] if cur.description else []

			# All sibling sites under this account, ordered by employees desc
			cur.execute(
				f"SELECT * FROM {sites_table} WHERE account_id = %s "
				f"ORDER BY {emp_num_sql} DESC;",
				[account_id],
			)
			sites = cur.fetchall()
			site_columns = [d.name for d in cur.description] if cur.description else []

			site_ids = [str(s["site_id"]) for s in sites]
			if not site_ids:
				return jsonify({"error": f"No sites for account_id {account_id}."}), 404

			# Products joined with lookup
			cur.execute(
				f"SELECT st.site_id, st.product_id, "
				f"       COALESCE(tl.product, st.product) AS product, "
				f"       COALESCE(tl.product_vendor, st.product_vendor) AS product_vendor, "
				f"       tl.product_category, tl.product_series "
				f"FROM {tech_table} st "
				f"LEFT JOIN {lookup_table} tl ON st.product_id = tl.product_id "
				f"WHERE st.site_id = ANY(%s::text[]);",
				[site_ids],
			)
			product_rows = cur.fetchall()
	except Exception as exc:  # pragma: no cover
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			try:
				conn.close()
			except Exception:
				pass

	# Group products by site
	products_by_site = {sid: [] for sid in site_ids}
	# Flat list (one row per site/product) for the products Tabulator
	products_flat = []
	site_name_by_id = {str(s["site_id"]): s.get("site_name") for s in sites}
	for r in product_rows:
		sid = str(r["site_id"])
		if sid not in products_by_site:
			continue
		entry = {
			"site_id": sid,
			"site_name": site_name_by_id.get(sid),
			"product_id": r.get("product_id"),
			"product": r.get("product"),
			"product_vendor": r.get("product_vendor"),
			"product_category": r.get("product_category"),
			"product_series": r.get("product_series"),
		}
		products_by_site[sid].append(entry)
		products_flat.append(entry)

	# Add product_count to each site row for display
	for s in sites:
		sid = str(s["site_id"])
		s["product_count"] = len(products_by_site.get(sid, []))
	if "product_count" not in site_columns:
		site_columns = list(site_columns) + ["product_count"]

	# Top site within this account: prefer site_type=UH, then HQ, then any
	# other type; tie-break by highest site_revenue_usd.
	top_site_id = None
	if sites:
		def _rev(s):
			v = s.get("site_revenue_usd")
			try:
				return float(v) if v not in (None, "") else 0.0
			except (TypeError, ValueError):
				return 0.0

		def _rank(s):
			t = (s.get("site_type") or "").strip().upper()
			if t == "UH":
				return 0
			if t == "HQ":
				return 1
			return 2

		top_site = min(sites, key=lambda s: (_rank(s), -_rev(s)))
		top_site_id = str(top_site.get("site_id"))

	return jsonify({
		"year": year,
		"selected_site_id": site_id,
		"account_id": account_id,
		"account": account,
		"account_columns": account_columns,
		"sites": sites,
		"site_columns": site_columns,
		"products": products_flat,
		"top_site_id": top_site_id,
	})


@app.route("/cpe-mapping")
def cpe_mapping():
	"""CPE Mapping browser page."""
	return render_template("cpe_mapping.html")


@app.route("/api/cpe-mapping")
def cpe_mapping_api():
	"""JSON API: return tech_with_cpe_mapping.csv data."""
	csv_path = Path(__file__).parent / "data" / "tech_cve" / "tech_with_cpe_mapping.csv"
	rows = []
	try:
		with open(csv_path, newline="", encoding="utf-8") as f:
			reader = csv.DictReader(f)
			for row in reader:
				rows.append(row)
	except FileNotFoundError:
		return jsonify({"error": "CSV file not found."}), 404
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	return jsonify(rows)


@app.route("/cve-summary")
def cve_summary():
	"""CVE Summary browser page."""
	return render_template("cve_summary.html")


@app.route("/api/cve-summary")
def cve_summary_api():
	"""JSON API: return tech_cve_summary.csv data."""
	csv_path = Path(__file__).parent / "data" / "tech_cve" / "tech_cve_summary.csv"
	rows = []
	try:
		with open(csv_path, newline="", encoding="utf-8") as f:
			reader = csv.DictReader(f)
			for row in reader:
				# Convert numeric fields
				for k in ("total_cves", "critical", "high", "medium", "low"):
					try:
						row[k] = int(row[k])
					except (KeyError, ValueError, TypeError):
						pass
				rows.append(row)
	except FileNotFoundError:
		return jsonify({"error": "CSV file not found."}), 404
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	return jsonify(rows)


# ---------------------------------------------------------------------------
# General Info CSV browsers
# ---------------------------------------------------------------------------

# Datasets available under data/swdb_general_info. Order controls the nav menu.
GENERAL_INFO_DATASETS = {
	"enterprises-counts": {
		"file": "enterprises_counts.csv",
		"title": "Enterprises Counts",
		"template": "enterprises_counts.html",
	},
	"universe-installs": {
		"file": "swdb_universe_installs.csv",
		"title": "Universe Installs 2022",
		"template": "general_info.html",
		"dedupe": True,
	},
	"universe-installs-2016": {
		"file": "universe_install_2016.csv",
		"title": "Universe Installs 2016",
		"description": (
			"Installed base for 2016: every vendor product with its total sites, "
			"US sites, total enterprises and US enterprises."
		),
		"template": "general_info.html",
		"dedupe": True,
		"text_cols": ["ProductId"],
		"cards": [
			{"label": "Products", "agg": "count"},
			{"label": "Vendors", "field": "VendorName", "agg": "distinct"},
			{"label": "Total Sites", "field": "Total Sites", "agg": "sum"},
			{"label": "Total Enterprises", "field": "Total Enterprises", "agg": "sum"},
		],
	},
	"universe-installs-2020": {
		"file": "universe_installs_2020.csv",
		"title": "Universe Installs 2020",
		"description": (
			"Installed base for 2020: every vendor product with its total sites, "
			"US sites, total enterprises and US enterprises."
		),
		"template": "general_info.html",
		"dedupe": True,
		"text_cols": ["ProductId"],
		"cards": [
			{"label": "Products", "agg": "count"},
			{"label": "Vendors", "field": "VendorName", "agg": "distinct"},
			{"label": "Total Sites", "field": "Total Sites", "agg": "sum"},
			{"label": "Total Enterprises", "field": "Total Enterprises", "agg": "sum"},
		],
	},
	"universe-installs-2023": {
		"file": "universe_installs_2023.csv",
		"title": "Universe Installs 2023",
		"description": (
			"Installed base for 2023 (CCID v5.0): every technology with its vendor, "
			"category, series and number of company installs."
		),
		"template": "universe_installs_ccid.html",
		"client_side": True,
		"text_cols": ["tech_id"],
	},
	"universe-installs-2024": {
		"file": "universe_installs_2024.csv",
		"title": "Universe Installs 2024",
		"description": (
			"Installed base for 2024 (CCID v5.1): every technology with its vendor, "
			"category, series and number of company installs."
		),
		"template": "universe_installs_ccid.html",
		"client_side": True,
		"text_cols": ["tech_id"],
	},
	"universe-installs-2025": {
		"file": "universe_installs_2025.csv",
		"title": "Universe Installs 2025",
		"description": (
			"Installed base for 2025 (C&C v5.2): every technology with its vendor, "
			"category, series and number of company installs."
		),
		"template": "universe_installs_ccid.html",
		"client_side": True,
		"text_cols": ["tech_id"],
	},
	"universe-installs-security": {
		"file": "universe_installs_security.csv",
		"title": "Universe Installs Enhanced",
		"template": "universe_install_security.html",
		"client_side": True,
		"dedupe": True,
		"text_cols": ["productid", "tabkeynewid"],
		"cards": [
			{"label": "Products", "agg": "count"},
			{"label": "Vendors", "field": "vendorname", "agg": "distinct"},
		],
	},
	"product-categories": {
		"file": "prodcatct-annotated-complete.csv",
		"title": "Security Products",
		"description": (
			"Curated list of the correct security product categories, mapping each "
			"vendor product to its validated security category (with Gartner market "
			"reference where available)."
		),
		"template": "general_info.html",
	},
	"years-regions": {
		"file": "swdb_years_regions_available.csv",
		"title": "Years & Regions Available",
		"template": "years_regions.html",
	},
	"product-counts": {
		"file": "prod_counts.csv",
		"title": "Product Counts",
		"template": "prod_counts.html",
	},
	"regional-tech-distribution": {
		"file": "regional_tech_distribution_2022.csv",
		"title": "Regional Tech Distribution 2022",
		"description": (
			"Enterprises per region in 2022, broken down by how many technologies "
			"they have installed (0, 1–50, 51–200, 201–1000, over 1000)."
		),
		"template": "regional_tech_distribution.html",
	},
}


def _load_general_info_df(filename, dedupe=False, text_cols=None):
	"""Load a general-info CSV with pandas and normalise it.

	- Reads everything as strings first (so IDs / codes are preserved).
	- Drops fully empty/unnamed columns.
	- Optionally removes duplicate rows.
	- Detects numeric columns (including values formatted like "696,761")
	  and converts them, returning the list of numeric column names.
	- Columns listed in ``text_cols`` are never converted (keeps leading zeros).
	"""

	text_cols = set(text_cols or [])
	csv_path = Path(__file__).parent / "data" / "swdb_general_info" / filename

	# Keep only the first occurrence of duplicated header names; pandas would
	# otherwise rename later ones to "name.1", which Tabulator reads as a nested path.
	with open(csv_path, newline="", encoding="utf-8") as fh:
		header = next(csv.reader(fh))
	seen = set()
	usecols = []
	for idx, name in enumerate(header):
		if name in seen:
			continue
		seen.add(name)
		usecols.append(idx)

	df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, usecols=usecols)

	# Some source files contain the header row repeated inside the data.
	# Drop any row whose values exactly match the column names.
	header_mask = df.apply(
		lambda r: list(r.astype(str)) == [str(c) for c in df.columns], axis=1
	)
	if header_mask.any():
		df = df[~header_mask].reset_index(drop=True)

	if dedupe:
		df = df.drop_duplicates().reset_index(drop=True)

	# Drop unnamed / empty header columns that carry no data
	drop_cols = []
	for col in df.columns:
		if str(col).strip() == "" or str(col).startswith("Unnamed"):
			if (df[col].astype(str).str.strip() == "").all():
				drop_cols.append(col)
	if drop_cols:
		df = df.drop(columns=drop_cols)

	numeric_cols = []
	for col in df.columns:
		if col in text_cols:
			continue
		stripped = df[col].astype(str).str.strip()
		non_empty = stripped[stripped != ""]
		if non_empty.empty:
			continue
		# Remove thousands separators before attempting numeric conversion
		cleaned = non_empty.str.replace(",", "", regex=False)
		converted = pd.to_numeric(cleaned, errors="coerce")
		if converted.notna().all():
			full = df[col].astype(str).str.strip().str.replace(",", "", regex=False)
			df[col] = pd.to_numeric(full, errors="coerce")
			numeric_cols.append(col)

	return df, numeric_cols


@app.route("/general-info/<slug>")
def general_info(slug):
	"""Render a CSV browser page for one of the general-info datasets."""
	dataset = GENERAL_INFO_DATASETS.get(slug)
	if dataset is None:
		abort(404)

	template = dataset.get("template", "general_info.html")
	context = {
		"slug": slug,
		"title": dataset["title"],
		"description": dataset.get("description"),
		"cards": dataset.get("cards"),
		"datasets": GENERAL_INFO_DATASETS,
	}

	# Pretty, server-rendered presentation pages get their data up-front.
	if template != "general_info.html" and not dataset.get("client_side"):
		try:
			df, numeric_cols = _load_general_info_df(
				dataset["file"],
				dedupe=dataset.get("dedupe", False),
				text_cols=dataset.get("text_cols"),
			)
			df = df.where(pd.notnull(df), None)
			context["columns"] = [
				{"field": str(c), "numeric": c in numeric_cols} for c in df.columns
			]
			context["rows"] = df.to_dict(orient="records")
		except Exception as exc:  # pragma: no cover
			context["error"] = str(exc)

	return render_template(template, **context)


@app.route("/api/general-info/<slug>")
def general_info_api(slug):
	"""JSON API: return the requested general-info CSV as records + metadata."""
	dataset = GENERAL_INFO_DATASETS.get(slug)
	if dataset is None:
		return jsonify({"error": "Unknown dataset."}), 404

	try:
		df, numeric_cols = _load_general_info_df(
			dataset["file"],
			dedupe=dataset.get("dedupe", False),
			text_cols=dataset.get("text_cols"),
		)
	except FileNotFoundError:
		return jsonify({"error": "CSV file not found."}), 404
	except Exception as exc:  # pragma: no cover - simple error surface
		return jsonify({"error": str(exc)}), 500

	# Replace NaN with None so the JSON is valid
	df = df.where(pd.notnull(df), None)

	columns = [
		{"field": str(col), "numeric": col in numeric_cols}
		for col in df.columns
	]
	rows = df.to_dict(orient="records")
	return jsonify({"columns": columns, "rows": rows})


# ---------------------------------------------------------------------------
# Database tables catalog
# ---------------------------------------------------------------------------

# Static rule takes precedence over the /general-info/<slug> converter rule.
@app.route("/general-info/db-tables")
def db_tables():
	"""Page listing every table in the database with its catalog information."""
	return render_template("db_tables.html", title="Database Tables")


@app.route("/api/db-tables")
def db_tables_api():
	"""JSON API: catalog information for every table in the database."""

	sql = """
		SELECT
			n.nspname                                   AS schema,
			c.relname                                   AS table_name,
			CASE c.relkind
				WHEN 'r' THEN 'table'
				WHEN 'p' THEN 'partitioned table'
				WHEN 'v' THEN 'view'
				WHEN 'm' THEN 'materialized view'
				WHEN 'f' THEN 'foreign table'
			END                                         AS object_type,
			pg_get_userbyid(c.relowner)                 AS owner,
			c.reltuples::bigint                         AS estimated_rows,
			(SELECT count(*)
			   FROM pg_attribute a
			  WHERE a.attrelid = c.oid
			    AND a.attnum > 0
			    AND NOT a.attisdropped)                 AS columns,
			(SELECT count(*) FROM pg_index i WHERE i.indrelid = c.oid) AS indexes,
			pg_total_relation_size(c.oid)               AS total_bytes,
			pg_relation_size(c.oid)                     AS data_bytes,
			pg_indexes_size(c.oid)                      AS index_bytes,
			pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
			obj_description(c.oid, 'pg_class')          AS description
		FROM pg_class c
		JOIN pg_namespace n ON n.oid = c.relnamespace
		WHERE c.relkind IN ('r', 'p', 'v', 'm', 'f')
		  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
		  AND n.nspname NOT LIKE 'pg_toast%'
		ORDER BY n.nspname, c.relname;
	"""

	try:
		conn = get_db_connection()
		with conn:
			with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
				cur.execute(sql)
				rows = [dict(r) for r in cur.fetchall()]
		conn.close()
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500

	return jsonify({"rows": rows})


@app.route("/api/db-tables/columns")
def db_table_columns_api():
	"""JSON API: column details for a single table."""

	schema = request.args.get("schema", "").strip()
	table = request.args.get("table", "").strip()
	if not schema or not table:
		return jsonify({"error": "Both 'schema' and 'table' are required."}), 400

	sql = """
		SELECT
			ordinal_position   AS position,
			column_name        AS column,
			data_type          AS type,
			character_maximum_length AS max_length,
			numeric_precision,
			numeric_scale,
			is_nullable        AS nullable,
			column_default     AS default_value
		FROM information_schema.columns
		WHERE table_schema = %s AND table_name = %s
		ORDER BY ordinal_position;
	"""

	try:
		conn = get_db_connection()
		with conn:
			with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
				cur.execute(sql, (schema, table))
				rows = [dict(r) for r in cur.fetchall()]
		conn.close()
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500

	return jsonify({"rows": rows})


# ---------------------------------------------------------------------------
# Domain names (accounts vs sites)
# ---------------------------------------------------------------------------

DOMAIN_NAMES_DIR = Path(__file__).parent / "data" / "domain_names"
DOMAIN_PRESENCE = ["Both", "Accounts only", "Sites only"]
# Filter values offered to the UI; the composite ones span two presence categories.
DOMAIN_PRESENCE_FILTERS = {
	"In accounts": ["Both", "Accounts only"],
	"In sites": ["Both", "Sites only"],
	"Both": ["Both"],
	"Accounts only": ["Accounts only"],
	"Sites only": ["Sites only"],
}
DOMAIN_NUM_COLS = {"total_accounts", "total_sites"}
DOMAIN_MAX_PAGE_SIZE = 500

_domain_names_df = None
_domain_names_lock = threading.Lock()


def _load_domain_names_df():
	"""Outer-join the accounts and sites domain CSVs on the domain name (cached)."""
	global _domain_names_df
	with _domain_names_lock:
		if _domain_names_df is not None:
			return _domain_names_df

		accounts = pd.read_csv(
			DOMAIN_NAMES_DIR / "accounts_domains.csv", dtype={"account_url": str, "total_accounts": "Int64"},
		).rename(columns={"account_url": "domain"})
		sites = pd.read_csv(
			DOMAIN_NAMES_DIR / "sites_domains.csv", dtype={"site_url": str, "total_sites": "Int64"},
		).rename(columns={"site_url": "domain"})

		accounts = accounts.dropna(subset=["domain"]).drop_duplicates("domain")
		sites = sites.dropna(subset=["domain"]).drop_duplicates("domain")

		df = accounts.merge(sites, on="domain", how="outer", indicator=True)
		df["presence"] = df["_merge"].map({
			"both": "Both", "left_only": "Accounts only", "right_only": "Sites only",
		}).astype(pd.CategoricalDtype(DOMAIN_PRESENCE))
		df = df.drop(columns="_merge")
		df["total_accounts"] = df["total_accounts"].fillna(0).astype("int64")
		df["total_sites"] = df["total_sites"].fillna(0).astype("int64")
		df = df[["domain", "presence", "total_accounts", "total_sites"]].sort_values("domain", kind="stable")
		_domain_names_df = df.reset_index(drop=True)
		return _domain_names_df


def _apply_domain_filters(df, args):
	raw = (args.get("f_domain") or "").strip()
	if raw:
		df = df[df["domain"].str.contains(re.escape(raw), case=False, na=False)]
	raw = (args.get("f_presence") or "").strip()
	if raw in DOMAIN_PRESENCE_FILTERS:
		df = df[df["presence"].isin(DOMAIN_PRESENCE_FILTERS[raw])]
	for col in DOMAIN_NUM_COLS:
		raw = (args.get(f"f_{col}") or "").strip()
		m = _NUM_FILTER_RE.match(raw) if raw else None
		if not m:
			continue
		op, target = m.group(1) or "=", float(m.group(2))
		s = df[col]
		mask = {"<": s < target, ">": s > target, "<=": s <= target, ">=": s >= target, "=": s == target}[op]
		df = df[mask]
	return df


def _sort_domain_df(df, args):
	sort = args.get("sort", "")
	if sort in df.columns:
		df = df.sort_values(sort, ascending=(args.get("dir", "asc") != "desc"), kind="stable")
	return df


def _domain_stats(df):
	counts = df["presence"].value_counts()
	both = int(counts.get("Both", 0))
	accounts_only = int(counts.get("Accounts only", 0))
	sites_only = int(counts.get("Sites only", 0))
	return {
		"domains": int(len(df)),
		"in_accounts": both + accounts_only,
		"in_sites": both + sites_only,
		"both": both,
		"accounts_only": accounts_only,
		"sites_only": sites_only,
		"total_accounts": int(df["total_accounts"].sum()),
		"total_sites": int(df["total_sites"].sum()),
	}


# First load takes ~15s (10M CSV rows); warm the cache so the first visitor doesn't wait.
threading.Thread(target=_load_domain_names_df, daemon=True).start()


@app.route("/general-info/domain-names")
def domain_names():
	return render_template(
		"domain_names.html", title="Domain Names", presence=list(DOMAIN_PRESENCE_FILTERS),
	)


@app.route("/api/domain-names/data")
def domain_names_data_api():
	"""Server-side paginated / filtered / sorted domains plus stats on the filtered set."""
	try:
		page = max(int(request.args.get("page", 1)), 1)
		size = min(max(int(request.args.get("size", 50)), 1), DOMAIN_MAX_PAGE_SIZE)
	except (TypeError, ValueError):
		return jsonify({"error": "page and size must be numbers."}), 400

	try:
		df = _load_domain_names_df()
	except FileNotFoundError as exc:
		return jsonify({"error": f"CSV file not found: {exc}"}), 404

	total_all = len(df)
	df = _sort_domain_df(_apply_domain_filters(df, request.args), request.args)

	total = len(df)
	last_page = max((total + size - 1) // size, 1)
	page = min(page, last_page)
	chunk = df.iloc[(page - 1) * size: page * size]
	chunk = chunk.assign(presence=chunk["presence"].astype(str))

	return jsonify({
		"data": chunk.to_dict(orient="records"),
		"last_page": last_page,
		"last_row": total,
		"total_all": total_all,
		"stats": _domain_stats(df),
	})


@app.route("/api/domain-names/download")
def domain_names_download():
	"""CSV of the filtered (and sorted) domains."""
	df = _sort_domain_df(_apply_domain_filters(_load_domain_names_df(), request.args), request.args)

	def generate():
		yield df.iloc[0:0].to_csv(index=False)
		for start in range(0, len(df), 50000):
			yield df.iloc[start:start + 50000].to_csv(index=False, header=False)

	return Response(
		generate(),
		mimetype="text/csv",
		headers={"Content-Disposition": "attachment; filename=domain_names.csv"},
	)


# ---------------------------------------------------------------------------
# NIST Categories (Australia / United States)
# ---------------------------------------------------------------------------

NIST_PHASES = ["Identify", "Protect", "Detect", "Respond", "Recover"]

NIST_COUNTRIES = {
	"australia": {
		"label": "Australia",
		"accounts": "australia_2022_accounts",
		"sites": "australia_2022_sites",
		"technologies": "australia_2022_technologies",
		"controls": "australia_nist_controls",
	},
	"usa": {
		"label": "United States",
		"accounts": "usa_2022_accounts",
		"sites": "usa_2022_sites",
		"technologies": "usa_2022_sites_technology",
		"controls": "usa_2022_nist_controls",
	},
	# all_2022_* are UNION ALL views over the regional tables; the same account
	# can appear in several regions, so accounts are de-duplicated on build.
	"all": {
		"label": "All Regions",
		"accounts": "all_2022_accounts",
		"sites": "all_2022_sites",
		"technologies": "all_2022_sites_technology",
		"controls": "all_2022_nist_controls",
		"phases_table": "all_2022_nist_phases",
		"extra_columns": ["region", "account_country"],
	},
}

NIST_BASE_COLUMNS = [
	"account_id", "account_name", "account_trade_name", "account_url",
	"n_controls", "n_nist_phases", "account_employees", "account_city",
	"account_revenue_usd", "account_state", "num_sites",
	"has_identify", "has_protect", "has_detect", "has_respond", "has_recover",
	"has_uncategorized",
]
NIST_NUM_COLS = {"n_controls", "n_nist_phases", "account_employees", "account_revenue_usd", "num_sites"}
NIST_BOOL_COLS = {c for c in NIST_BASE_COLUMNS if c.startswith("has_")}


def _nist_columns(cfg):
	"""Column order for a country: base columns, extras inserted after account_state."""
	cols = list(NIST_BASE_COLUMNS)
	pos = cols.index("account_state") + 1
	for i, c in enumerate(cfg.get("extra_columns", [])):
		cols.insert(pos + i, c)
	return cols


def _nist_text_cols(cols):
	return [c for c in cols if c not in NIST_NUM_COLS and c not in NIST_BOOL_COLS]

NIST_CACHE_DIR = Path(__file__).parent / "data" / "nist_cache"
NIST_MAX_PAGE_SIZE = 500

# The build scans every technology row (13M for AU, 415M for US), so the
# result is persisted to parquet and built in a background thread.
_nist_cache = {}
_nist_lock = threading.Lock()


def _nist_country(country):
	cfg = NIST_COUNTRIES.get(country)
	if not cfg:
		abort(404)
	return cfg


def _nist_state(country):
	with _nist_lock:
		return _nist_cache.setdefault(country, {
			"df": None, "built_at": None, "building": False, "error": None,
		})


def _nist_cache_path(country):
	return NIST_CACHE_DIR / f"{country}_nist_categories.parquet"


def _build_nist_df(cfg):
	"""Accounts + NIST controls + per-account NIST phase flags + site counts."""

	columns = _nist_columns(cfg)
	extra = cfg.get("extra_columns", [])
	# In multi-region views an account can exist in several regions: list them all.
	extra_sql = "".join(
		f",\n\t\t       reg.regions AS region" if c == "region" else f",\n\t\t       acc.{c}"
		for c in extra
	)
	region_join = (
		f"""JOIN (SELECT account_id, string_agg(DISTINCT region, ', ' ORDER BY region) AS regions
		      FROM {cfg['accounts']} GROUP BY account_id) AS reg ON reg.account_id = acc.account_id"""
		if "region" in extra else ""
	)
	# DISTINCT ON keeps one row per account when the source is a multi-region view.
	accounts_sql = f"""
		SELECT DISTINCT ON (acc.account_id)
		       acc.account_id,
		       acc.account_name,
		       acc.account_trade_name,
		       acc.account_url,
		       nist.n_controls,
		       acc.account_employees,
		       acc.account_city,
		       acc.account_revenue_usd,
		       acc.account_state{extra_sql}
		FROM {cfg['controls']} AS nist
		JOIN {cfg['accounts']} AS acc ON acc.account_id = nist.account_id
		{region_join}
		ORDER BY acc.account_id;
	"""
	sites_sql = f"""
		SELECT account_id, COUNT(DISTINCT site_id) AS num_sites
		FROM {cfg['sites']}
		GROUP BY account_id;
	"""
	# 'Multiple' and NULL phases on security products count as Uncategorized.
	if cfg.get("phases_table"):
		phases_sql = f"""
			SELECT account_id::text AS account_id,
			       COALESCE(NULLIF(nist_phase, 'Multiple'), 'Uncategorized') AS nist_phase
			FROM {cfg['phases_table']}
			GROUP BY 1, 2;
		"""
	else:
		phases_sql = f"""
			SELECT s.account_id,
			       COALESCE(NULLIF(u.nist_phase, 'Multiple'), 'Uncategorized') AS nist_phase
			FROM {cfg['technologies']} t
			JOIN universe_installs_enhanced u
			  ON u.productid::text = t.product_id AND u.security_product
			JOIN {cfg['sites']} s ON s.site_id = t.site_id
			GROUP BY 1, 2;
		"""

	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(accounts_sql)
			acc = pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
			cur.execute(sites_sql)
			sites = pd.DataFrame(cur.fetchall(), columns=["account_id", "num_sites"])
			cur.execute(phases_sql)
			phases = pd.DataFrame(cur.fetchall(), columns=["account_id", "nist_phase"])
	finally:
		conn.close()

	flags = (
		pd.crosstab(phases["account_id"], phases["nist_phase"]).astype(bool)
		if not phases.empty else pd.DataFrame()
	)
	for phase in NIST_PHASES + ["Uncategorized"]:
		if phase not in flags.columns:
			flags[phase] = False
	flags = flags.rename(columns={p: f"has_{p.lower()}" for p in NIST_PHASES + ["Uncategorized"]})
	flags["n_nist_phases"] = flags[[f"has_{p.lower()}" for p in NIST_PHASES]].sum(axis=1).astype(int)
	flags = flags.reset_index()

	df = acc.merge(sites, on="account_id", how="left").merge(flags, on="account_id", how="left")

	for col in _nist_text_cols(columns):
		df[col] = df[col].fillna("").astype(str)
	for col in ("n_controls", "num_sites", "n_nist_phases"):
		df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
	for col in ("account_employees", "account_revenue_usd"):
		df[col] = pd.to_numeric(df[col].replace("", None), errors="coerce").astype("Int64")
	for col in NIST_BOOL_COLS:
		df[col] = df[col].eq(True)

	df = df.sort_values(["n_controls", "n_nist_phases", "account_name"], ascending=[False, False, True])
	return df[columns].reset_index(drop=True)


def _nist_start_build(country, build_fn=None):
	"""Build the dataset for `country` in a background thread.

	`build_fn` defaults to the NIST categories build; other datasets sharing the
	same cache machinery (e.g. hacked sites) pass their own.
	"""
	if build_fn is None:
		cfg = _nist_country(country)
		build_fn = lambda: _build_nist_df(cfg)  # noqa: E731
	state = _nist_state(country)
	with _nist_lock:
		if state["building"]:
			return
		state["building"] = True
		state["error"] = None
		state["started_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

	def run():
		try:
			df = build_fn()
			NIST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
			df.to_parquet(_nist_cache_path(country), index=False)
			state["df"] = df
			state["built_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
		except Exception as exc:  # pragma: no cover
			state["error"] = str(exc)
		finally:
			state["building"] = False

	threading.Thread(target=run, daemon=True, name=f"nist-build-{country}").start()


def _nist_get_df(country, refresh=False, build_fn=None):
	"""Return the cached DataFrame, or None if it is (now) being built."""
	state = _nist_state(country)
	if refresh:
		_nist_start_build(country, build_fn)
		return None
	if state["df"] is not None:
		return state["df"]
	path = _nist_cache_path(country)
	if path.exists() and not state["building"]:
		df = pd.read_parquet(path)
		state["df"] = df
		state["built_at"] = datetime.fromtimestamp(
			path.stat().st_mtime, tz=timezone.utc
		).isoformat(timespec="seconds")
		return df
	_nist_start_build(country, build_fn)
	return None


_NUM_FILTER_RE = re.compile(r"^(<=|>=|<|>|=)?\s*(-?\d+(?:\.\d+)?)$")


def _apply_nist_filters(df, args, num_cols=NIST_NUM_COLS, bool_cols=NIST_BOOL_COLS):
	"""Apply `f_<column>` query params to the DataFrame."""
	for col in df.columns:
		raw = (args.get(f"f_{col}") or "").strip()
		if not raw:
			continue
		if col in num_cols:
			m = _NUM_FILTER_RE.match(raw)
			if not m:
				continue
			op, target = m.group(1) or "=", float(m.group(2))
			s = df[col]
			mask = {
				"<": s < target, ">": s > target, "<=": s <= target,
				">=": s >= target, "=": s == target,
			}[op]
			df = df[mask.fillna(False).astype(bool)]
		elif col in bool_cols:
			if raw.lower() in ("true", "false"):
				df = df[df[col] == (raw.lower() == "true")]
		else:
			df = df[df[col].str.contains(re.escape(raw), case=False, na=False)]
	return df


def _nist_stats(df):
	"""Cards + NIST coverage table (% of accounts) by firm-size bucket."""
	n = len(df)
	emp = df["account_employees"]
	bucket = pd.Series("unknown", index=df.index, dtype=object)
	bucket[(emp > 500).fillna(False).astype(bool)] = "gt500"
	bucket[((emp >= 10) & (emp <= 500)).fillna(False).astype(bool)] = "mid"
	bucket[(emp < 10).fillna(False).astype(bool)] = "lt10"

	metrics = {
		"identify": df["has_identify"],
		"protect": df["has_protect"],
		"detect": df["has_detect"],
		"respond": df["has_respond"],
		"recover": df["has_recover"],
		"uncategorized": df["has_uncategorized"],
		"ge1": df["n_nist_phases"] >= 1,
		"ge2": df["n_nist_phases"] >= 2,
		"ge3": df["n_nist_phases"] >= 3,
		"ge4": df["n_nist_phases"] >= 4,
		"eq5": df["n_nist_phases"] == 5,
	}
	mdf = pd.DataFrame(metrics).astype(int)
	totals = mdf.sum()
	by_bucket = mdf.groupby(bucket).sum() if n else pd.DataFrame(columns=mdf.columns)
	denoms = bucket.value_counts().to_dict() if n else {}

	def pct(num, den):
		return round(100.0 * num / den, 1) if den else None

	table = {}
	for key in metrics:
		table[key] = {"all": pct(int(totals[key]), n)}
		for b in ("gt500", "mid", "lt10"):
			num = int(by_bucket.loc[b, key]) if b in by_bucket.index else 0
			table[key][b] = pct(num, int(denoms.get(b, 0)))

	return {
		"accounts": int(n),
		"avg_controls": round(float(df["n_controls"].mean()), 2) if n else 0,
		"avg_phases": round(float(df["n_nist_phases"].mean()), 2) if n else 0,
		"total_sites": int(df["num_sites"].sum()) if n else 0,
		"denominators": {
			"all": int(n),
			"gt500": int(denoms.get("gt500", 0)),
			"mid": int(denoms.get("mid", 0)),
			"lt10": int(denoms.get("lt10", 0)),
			"unknown": int(denoms.get("unknown", 0)),
		},
		"table": table,
	}


def _nist_building_response(country):
	state = _nist_state(country)
	if state["error"]:
		return jsonify({"error": f"Dataset build failed: {state['error']}"}), 500
	return jsonify({
		"status": "building",
		"started_at": state.get("started_at"),
		"message": "Dataset is being built from the database; this can take several minutes for large countries.",
	}), 202


@app.route("/nist-categories/<country>")
def nist_categories(country):
	cfg = _nist_country(country)
	columns = _nist_columns(cfg)
	column_meta = [
		{"field": c, "type": "num" if c in NIST_NUM_COLS else "bool" if c in NIST_BOOL_COLS else "text"}
		for c in columns
	]
	return render_template(
		"nist_categories.html",
		country=country,
		country_label=cfg["label"],
		column_meta=column_meta,
	)


@app.route("/api/nist-categories/<country>/data")
def nist_categories_data_api(country):
	"""Server-side paginated / filtered / sorted rows plus stats on the filtered set."""
	_nist_country(country)
	refresh = request.args.get("refresh") == "1"
	df = _nist_get_df(country, refresh=refresh)
	if df is None:
		return _nist_building_response(country)

	try:
		page = max(int(request.args.get("page", 1)), 1)
		size = min(max(int(request.args.get("size", 50)), 1), NIST_MAX_PAGE_SIZE)
	except (TypeError, ValueError):
		return jsonify({"error": "page and size must be numbers."}), 400

	total_all = len(df)
	df = _apply_nist_filters(df, request.args)

	sort = request.args.get("sort", "")
	direction = request.args.get("dir", "asc")
	if sort in df.columns:
		df = df.sort_values(sort, ascending=(direction != "desc"), na_position="last", kind="stable")

	stats = _nist_stats(df)
	total = len(df)
	last_page = max((total + size - 1) // size, 1)
	page = min(page, last_page)
	chunk = df.iloc[(page - 1) * size: page * size]
	rows = chunk.astype(object).where(chunk.notna(), None).to_dict(orient="records")

	return jsonify({
		"data": rows,
		"last_page": last_page,
		"last_row": total,
		"total_all": total_all,
		"stats": stats,
		"built_at": _nist_state(country)["built_at"],
	})


@app.route("/api/nist-categories/<country>/download")
def nist_categories_download(country):
	"""CSV of the filtered (and sorted) dataset."""
	cfg = _nist_country(country)
	df = _nist_get_df(country)
	if df is None:
		return _nist_building_response(country)

	df = _apply_nist_filters(df, request.args)
	sort = request.args.get("sort", "")
	direction = request.args.get("dir", "asc")
	if sort in df.columns:
		df = df.sort_values(sort, ascending=(direction != "desc"), na_position="last", kind="stable")

	def generate():
		yield df.iloc[0:0].to_csv(index=False)
		for start in range(0, len(df), 50000):
			yield df.iloc[start:start + 50000].to_csv(index=False, header=False)

	filename = f"{country}_nist_categories.csv"
	return Response(
		generate(),
		mimetype="text/csv",
		headers={"Content-Disposition": f"attachment; filename={filename}"},
	)


def _nist_regions_filter(cfg, alias):
	"""SQL fragment + params restricting a multi-region view to the account's regions.

	The constant `region` per UNION ALL branch lets PostgreSQL skip the other
	regional tables entirely.
	"""
	if "region" not in cfg.get("extra_columns", []):
		return "", {}
	regions = [r.strip() for r in request.args.get("regions", "").split(",") if r.strip()]
	if not regions:
		return "", {}
	return f" AND {alias}.region = ANY(%(regions)s)", {"regions": regions}


@app.route("/api/nist-categories/<country>/account-sites")
def nist_account_sites_api(country):
	"""JSON API: every site (all columns) linked to an account."""
	cfg = _nist_country(country)
	account_id = request.args.get("account_id", "").strip()
	if not account_id:
		return jsonify({"error": "account_id is required."}), 400
	region_sql, region_params = _nist_regions_filter(cfg, "s")

	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute(
				f"SELECT * FROM {cfg['sites']} s WHERE s.account_id = %(account_id)s{region_sql} "
				f"ORDER BY COALESCE(NULLIF(site_employees, '')::bigint, 0) DESC, site_name;",
				{"account_id": account_id, **region_params},
			)
			rows = [dict(r) for r in cur.fetchall()]
			columns = [d.name for d in cur.description] if cur.description else []
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			try:
				conn.close()
			except Exception:
				pass

	return jsonify({"account_id": account_id, "columns": columns, "rows": rows})


@app.route("/api/nist-categories/<country>/account-technologies")
def nist_account_technologies_api(country):
	"""JSON API: every technology installed by an account, enriched with the
	NIST phase / security category from `universe_installs_enhanced`.
	"""
	cfg = _nist_country(country)
	account_id = request.args.get("account_id", "").strip()
	if not account_id:
		return jsonify({"error": "account_id is required."}), 400
	sites_region_sql, region_params = _nist_regions_filter(cfg, "s")
	tech_region_sql, _ = _nist_regions_filter(cfg, "t")

	sql = f"""
		SELECT t.product_id,
		       COALESCE(u.vendorname, t.product_vendor)  AS vendor,
		       COALESCE(u.product, t.product)            AS product,
		       u.productcategory,
		       u.actualcat                               AS security_category,
		       CASE WHEN u.security_product
		            THEN COALESCE(NULLIF(u.nist_phase, 'Multiple'), 'Uncategorized')
		       END                                       AS nist_phase,
		       COALESCE(u.security_product, FALSE)       AS security_product,
		       COALESCE(u.is_open_source, FALSE)         AS is_open_source,
		       COUNT(DISTINCT t.site_id)                 AS n_sites
		FROM {cfg['sites']} s
		JOIN {cfg['technologies']} t ON t.site_id = s.site_id{tech_region_sql}
		LEFT JOIN universe_installs_enhanced u
		       ON u.productid = NULLIF(t.product_id, '')::int
		WHERE s.account_id = %(account_id)s{sites_region_sql}
		GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
		ORDER BY n_sites DESC, product;
	"""
	account_sql = f"""
		SELECT account_id, account_name, account_url, account_city,
		       account_state, account_employees, account_nb_sites
		FROM {cfg['accounts']} acc
		WHERE acc.account_id = %(account_id)s{_nist_regions_filter(cfg, 'acc')[0]}
		LIMIT 1;
	"""

	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			params = {"account_id": account_id, **region_params}
			cur.execute(account_sql, params)
			account = cur.fetchone()
			cur.execute(sql, params)
			rows = [dict(r) for r in cur.fetchall()]
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			try:
				conn.close()
			except Exception:
				pass

	df = pd.DataFrame(rows, columns=[
		"product_id", "vendor", "product", "productcategory", "security_category",
		"nist_phase", "security_product", "is_open_source", "n_sites",
	])
	df["nist_phase"] = df["nist_phase"].fillna("").replace({None: ""})
	for col in ("vendor", "product", "productcategory", "security_category"):
		df[col] = df[col].fillna("")

	security = df[df["security_product"] == True]  # noqa: E712 - pandas mask
	phases = {p for p in df["nist_phase"].tolist() if p in NIST_PHASES}
	phase_counts = (
		df.loc[df["nist_phase"] != "", "nist_phase"].value_counts().to_dict()
		if not df.empty else {}
	)

	return jsonify({
		"account": dict(account) if account else {"account_id": account_id},
		"summary": {
			"technologies": int(len(df)),
			"security_products": int(len(security)),
			"nist_phases": len(phases),
			"phase_counts": {k: int(v) for k, v in phase_counts.items()},
		},
		"rows": df.to_dict(orient="records"),
	})


# ---------------------------------------------------------------------------
# Hacked sites (ransomware victims / municipalities) vs NIST categories
# ---------------------------------------------------------------------------

# Each dataset is a precomputed "<domains> x all_2022_sites x technologies"
# table (see task SQL). Two views are offered: one row per SWDB site ("sites")
# and one row per domain collapsing all its matched sites ("domains").
# `extras_sql` must return one row per raw domain value (aliased `domain`)
# with the dataset-specific descriptive columns listed in `extras`.
HACKED_DATASETS = {
	"victims": {
		"label": "Ransomware Victims",
		"table": "leak_victims_joined_with_hacked_flag_and_swdb_with_tech",
		"domains_table": "leak_victims_joined_with_hacked_flag_and_swdb",
		"domain_col": '"Website domain"',
		"hacked_sql": "hacked",
		# Raw source list used by the account-level matching.
		"source_table": "leak_victims_joined_with_hacked_flag",
		"source_domain_col": '"Website domain"',
		"extras": [
			("leak_group", "text"), ("ransomwarelive_group", "text"), ("first_seen", "text"),
			("published", "text"), ("country", "text"),
		],
		"extras_sql": """
			SELECT "Website domain" AS domain,
			       string_agg(DISTINCT NULLIF("Group", ''), ', ') AS leak_group,
			       string_agg(DISTINCT NULLIF(ransomwarelive_group, ''), ', ') AS ransomwarelive_group,
			       MIN(NULLIF("First seen", '')) AS first_seen,
			       MIN(NULLIF(published, '')) AS published,
			       string_agg(DISTINCT NULLIF(country, ''), ', ') AS country
			FROM leak_victims_joined_with_hacked_flag
			GROUP BY 1
		""",
	},
	"municipalities": {
		"label": "Municipalities",
		"table": "muni_matchpairs_with_swdb_with_tech",
		"domains_table": "muni_matchpairs_with_swdb",
		"domain_col": "muni_domain_name",
		"hacked_sql": "lower(hacked) = 'true'",
		"source_table": "municipalities_matchpairs",
		"source_domain_col": "domain",
		"extras": [
			("matchid", "text"), ("post_title", "text"), ("state", "text"), ("population", "num"),
			("government_service", "text"), ("likely_government_municipality", "text"),
			("group_name", "text"), ("discovered", "text"), ("published", "text"),
			("activity", "text"), ("country", "text"),
		],
		"extras_sql": """
			SELECT domain,
			       string_agg(DISTINCT matchid::text, ', ') AS matchid,
			       string_agg(DISTINCT NULLIF(post_title, ''), ' | ') AS post_title,
			       string_agg(DISTINCT NULLIF(state, ''), ', ') AS state,
			       MAX(population) AS population,
			       string_agg(DISTINCT NULLIF(goverment_service, ''), ', ') AS government_service,
			       string_agg(DISTINCT NULLIF(likely_government_municipality, ''), ', ') AS likely_government_municipality,
			       string_agg(DISTINCT NULLIF(group_name, ''), ', ') AS group_name,
			       MIN(NULLIF(discovered, '')) AS discovered,
			       MIN(NULLIF(published, '')) AS published,
			       string_agg(DISTINCT NULLIF(activity, ''), ', ') AS activity,
			       string_agg(DISTINCT NULLIF(country, ''), ', ') AS country
			FROM municipalities_matchpairs
			WHERE domain IS NOT NULL AND trim(domain) <> ''
			GROUP BY 1
		""",
	},
}

HACKED_PHASE_COLS = [f"has_{p.lower()}" for p in NIST_PHASES] + ["has_uncategorized"]

# Per-level column layout: (name, type). Extras are inserted after `hacked`.
HACKED_LEVELS = {
	"sites": {
		"label": "Sites",
		"controls_col": "n_controls",
		"phases_col": "n_nist_phases",
		"sites_col": None,
		"columns": [
			("domain", "text"), ("hacked", "bool"),
			("site_name", "text"), ("account_id", "text"), ("site_id", "text"),
			("site_type", "text"), ("region", "text"),
			("site_employees", "num"), ("site_ict_spending", "num"), ("site_revenue_usd", "num"),
			("n_technologies", "num"), ("n_controls", "num"), ("n_nist_phases", "num"),
		],
	},
	"domains": {
		"label": "Domains",
		"controls_col": "total_sec_products",
		"phases_col": "total_nist_categories",
		"sites_col": "total_sites",
		"columns": [
			("domain", "text"), ("hacked", "bool"),
			("total_sites", "num"), ("total_accounts", "num"),
			("total_employees", "num"), ("total_ict_spending", "num"), ("total_revenue_usd", "num"),
			("total_technologies", "num"), ("total_sec_products", "num"), ("total_nist_categories", "num"),
		],
	},
	"accounts": {
		"label": "Accounts",
		"controls_col": "n_controls",
		"phases_col": "n_nist_phases",
		"sites_col": "num_sites",
		"columns": [
			("domain", "text"), ("hacked", "bool"),
			("matched_on", "text"), ("match_tier", "num"), ("n_candidates", "num"), ("ambiguous", "bool"),
			("account_id", "text"), ("account_name", "text"), ("account_url", "text"), ("region", "text"),
			("account_country", "text"), ("account_state", "text"), ("account_pri_naics6_code", "text"),
			("account_employees", "num"), ("account_revenue_usd", "num"), ("account_nb_sites", "num"),
			("num_sites", "num"), ("n_technologies", "num"), ("n_controls", "num"), ("n_nist_phases", "num"),
		],
	},
}

# Host normalisation shared by the matching: strip scheme, www., path/port, lowercase.
HACKED_NORM_SQL = "lower(trim(regexp_replace(regexp_replace(trim({c}), '^(https?://)?(www\\.)?', ''), '[/:?#].*$', '')))"
HACKED_HOST_RE = r"^[a-z0-9-]+(\.[a-z0-9-]+)+$"
# Share of candidates' weight (sites) one account must hold to be taken as the parent.
HACKED_PARENT_SHARE = 0.8
ALL_2022_REGIONS = ["usa", "canada", "emea", "apac", "latam"]


def _hacked_dataset(key):
	cfg = HACKED_DATASETS.get(key)
	if not cfg:
		abort(404)
	return cfg


def _hacked_level(level):
	lv = HACKED_LEVELS.get(level)
	if not lv:
		abort(404)
	return lv


def _hacked_columns(cfg, level):
	"""Ordered (name, type) pairs for a dataset/level, extras after `hacked`."""
	cols = list(HACKED_LEVELS[level]["columns"])
	pos = [c for c, _ in cols].index("hacked") + 1
	cols[pos:pos] = list(cfg["extras"])
	return cols + [(c, "bool") for c in HACKED_PHASE_COLS]


def _hacked_col_sets(cfg, level):
	cols = _hacked_columns(cfg, level)
	return {c for c, t in cols if t == "num"}, {c for c, t in cols if t == "bool"}


def _hacked_cache_key(key, level):
	return key if level == "sites" else f"{key}_{level}"


def _hacked_summary_path(key, level="sites"):
	suffix = "_accounts" if level == "accounts" else ""
	return NIST_CACHE_DIR / f"{key}{suffix}_summary.json"


def _hacked_domain_tech_path(key):
	return NIST_CACHE_DIR / f"{key}_domain_technologies.parquet"


def _hacked_phase_flags_sql():
	flags = [f"bool_or(security_product AND nist_phase = '{p}') AS has_{p.lower()}" for p in NIST_PHASES]
	flags.append("bool_or(security_product AND COALESCE(nist_phase, 'Multiple') = 'Multiple') AS has_uncategorized")
	return ",\n\t\t       ".join(flags)


def _hacked_finish_df(df, cfg, level):
	"""Cast columns to their declared types and order them."""
	cols = _hacked_columns(cfg, level)
	lv = HACKED_LEVELS[level]
	for c, t in cols:
		if c not in df.columns:
			df[c] = None
		if t == "text":
			df[c] = df[c].fillna("").astype(str)
		elif t == "bool":
			df[c] = df[c].eq(True)
		elif c in ("n_technologies", "n_controls", "total_sites", "total_accounts",
		           "total_technologies", "total_sec_products", "num_sites", "match_tier", "n_candidates"):
			df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("int64")
		elif c != lv["phases_col"]:
			df[c] = pd.to_numeric(df[c].replace("", None), errors="coerce").round().astype("Int64")
	df[lv["phases_col"]] = df[[f"has_{p.lower()}" for p in NIST_PHASES]].sum(axis=1).astype("int64")
	sort_by = ["hacked", lv["controls_col"]] + (["site_name"] if level == "sites" else ["domain"])
	if level == "accounts":
		sort_by = ["ambiguous", "hacked", lv["controls_col"], "domain"]
		df = df.sort_values(sort_by, ascending=[True, False, False, True])
	else:
		df = df.sort_values(sort_by, ascending=[False, False, True])
	return df[[c for c, _ in cols]].reset_index(drop=True)


def _build_hacked_sites_df(cfg, key):
	"""One row per SWDB site: site info, hacked flag, technology / control counts
	and NIST phase flags. Domain-level totals are saved next to the parquet."""
	sql = f"""
		WITH per_site AS (
			SELECT {cfg['domain_col']} AS domain, site_name, account_id, site_id, site_type, region,
			       site_employees, site_ict_spending, site_revenue_usd,
			       {cfg['hacked_sql']} AS hacked,
			       COUNT(DISTINCT product_id) AS n_technologies,
			       COUNT(DISTINCT product_id) FILTER (WHERE security_product) AS n_controls,
			       {_hacked_phase_flags_sql()}
			FROM {cfg['table']}
			GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
		)
		SELECT p.*, x.*
		FROM per_site p
		LEFT JOIN ({cfg['extras_sql']}) x USING (domain);
	"""
	summary_sql = f"""
		SELECT COUNT(DISTINCT {cfg['domain_col']}) AS domains,
		       COUNT(DISTINCT {cfg['domain_col']}) FILTER (WHERE site_id IS NOT NULL) AS domains_matched,
		       COUNT(DISTINCT {cfg['domain_col']}) FILTER (WHERE {cfg['hacked_sql']}) AS domains_hacked
		FROM {cfg['domains_table']};
	"""
	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(sql)
			df = pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
			cur.execute(summary_sql)
			summary = dict(zip([d.name for d in cur.description], cur.fetchone()))
	finally:
		conn.close()

	df = df.loc[:, ~df.columns.duplicated()]
	NIST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	_hacked_summary_path(key).write_text(json.dumps({k: int(v or 0) for k, v in summary.items()}))
	return _hacked_finish_df(df, cfg, "sites")


def _build_hacked_domains_df(cfg, key):
	"""One row per domain collapsing every matched SWDB site (user's CTE logic):
	site totals summed over distinct sites, technologies counted once per domain.
	The distinct technology list per domain is saved to a side parquet for the modal."""
	sql = f"""
		WITH sites AS (
			SELECT DISTINCT {cfg['domain_col']} AS domain, site_id, account_id,
			       site_employees, site_ict_spending, site_revenue_usd
			FROM {cfg['table']}
		),
		site_totals AS (
			SELECT domain,
			       SUM(NULLIF(site_employees, '')::numeric)    AS total_employees,
			       SUM(NULLIF(site_ict_spending, '')::numeric) AS total_ict_spending,
			       SUM(NULLIF(site_revenue_usd, '')::numeric)  AS total_revenue_usd,
			       COUNT(DISTINCT account_id)                  AS total_accounts,
			       COUNT(DISTINCT site_id)                     AS total_sites
			FROM sites
			GROUP BY domain
		),
		tech_totals AS (
			SELECT {cfg['domain_col']} AS domain,
			       bool_or({cfg['hacked_sql']}) AS hacked,
			       COUNT(DISTINCT product_id) AS total_technologies,
			       COUNT(DISTINCT product_id) FILTER (WHERE security_product) AS total_sec_products,
			       {_hacked_phase_flags_sql()}
			FROM {cfg['table']}
			GROUP BY 1
		)
		SELECT t.*, s.total_employees, s.total_ict_spending, s.total_revenue_usd,
		       s.total_accounts, s.total_sites, x.*
		FROM tech_totals t
		JOIN site_totals s USING (domain)
		LEFT JOIN ({cfg['extras_sql']}) x USING (domain);
	"""
	tech_sql = f"""
		SELECT {cfg['domain_col']} AS domain, product_id, product_vendor AS vendor, product,
		       actualcat AS category, security_product, nist_phase,
		       MAX(product_confidence_ranking) AS confidence,
		       COUNT(DISTINCT site_id) AS n_sites
		FROM {cfg['table']}
		GROUP BY 1, 2, 3, 4, 5, 6, 7;
	"""
	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(sql)
			df = pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
			cur.execute(tech_sql)
			tech = pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
	finally:
		conn.close()

	for c in ("domain", "product_id", "vendor", "product", "category", "nist_phase", "confidence"):
		tech[c] = tech[c].fillna("").astype(str)
	tech["security_product"] = tech["security_product"].eq(True)
	tech["n_sites"] = pd.to_numeric(tech["n_sites"], errors="coerce").fillna(0).astype("int64")
	NIST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	tech.to_parquet(_hacked_domain_tech_path(key), index=False)
	_hacked_domain_tech_cache.pop(key, None)

	df = df.loc[:, ~df.columns.duplicated()]
	return _hacked_finish_df(df, cfg, "domains")


def _build_hacked_accounts_df(cfg, key):
	"""One row per source domain matched to a single SWDB account.

	Matching (persisted in table `domain_account_match`, source = key):
	  tier 1  account_url match, one candidate
	  tier 2  account_url match, several candidates, one holds >= 80% of their sites (parent)
	  tier 3  account_url match, ambiguous -> largest candidate kept, flagged
	  tier 4  no account_url hit; site_url match, one owning account
	  tier 5  site_url match, one account owns >= 80% of the matched sites
	  tier 6  site_url match, ambiguous -> largest kept, flagged
	Technology metrics come from the precomputed all_2022_nist_* tables plus a
	scan of the matched accounts' sites/technologies.
	"""
	norm_src = HACKED_NORM_SQL.format(c=cfg["source_domain_col"])
	norm_acc = HACKED_NORM_SQL.format(c="a.account_url")
	norm_site = HACKED_NORM_SQL.format(c="s.site_url")
	share = HACKED_PARENT_SHARE

	rank_sql = """
		SELECT *,
		       COUNT(*)      OVER (PARTITION BY domain) AS n_candidates,
		       SUM(weight)   OVER (PARTITION BY domain) AS total_weight,
		       ROW_NUMBER()  OVER (PARTITION BY domain ORDER BY weight DESC, account_id) AS rn
		FROM {src}
	"""
	tier_sql = f"""
		CASE WHEN n_candidates = 1 THEN {{base}}
		     WHEN total_weight > 0 AND weight >= {share} * total_weight THEN {{base}} + 1
		     ELSE {{base}} + 2 END
	"""

	steps = [
		f"""
		CREATE TEMP TABLE m_dom AS
		SELECT {norm_src} AS domain,
		       MIN({cfg['source_domain_col']}) AS domain_raw,
		       bool_or({cfg['hacked_sql']}) AS hacked
		FROM {cfg['source_table']}
		WHERE {cfg['source_domain_col']} IS NOT NULL AND {norm_src} ~ %(host_re)s
		GROUP BY 1;
		""",
		f"""
		CREATE TEMP TABLE m_acc AS
		SELECT m.domain, a.account_id,
		       MIN(a.account_name) AS account_name, MIN(a.account_url) AS account_url,
		       string_agg(DISTINCT a.region, ', ' ORDER BY a.region) AS region,
		       COALESCE(MAX(NULLIF(a.account_nb_sites, '')::numeric), 0) AS weight
		FROM all_2022_accounts a
		JOIN m_dom m ON {norm_acc} = m.domain
		GROUP BY 1, 2;
		""",
		f"""
		CREATE TEMP TABLE m_by_acc AS
		SELECT domain, account_id, account_name, account_url, region, 'account_url' AS matched_on,
		       {tier_sql.format(base=1)} AS match_tier, n_candidates
		FROM ({rank_sql.format(src='m_acc')}) r
		WHERE rn = 1;
		""",
		f"""
		CREATE TEMP TABLE m_site AS
		SELECT m.domain, s.account_id, COUNT(DISTINCT s.site_id) AS weight,
		       string_agg(DISTINCT s.region, ', ' ORDER BY s.region) AS region
		FROM all_2022_sites s
		JOIN m_dom m ON {norm_site} = m.domain
		WHERE NOT EXISTS (SELECT 1 FROM m_by_acc b WHERE b.domain = m.domain)
		GROUP BY 1, 2;
		""",
		f"""
		CREATE TEMP TABLE m_by_site AS
		SELECT r.domain, r.account_id, a.account_name, a.account_url, r.region, 'site_url' AS matched_on,
		       {tier_sql.format(base=4)} AS match_tier, n_candidates
		FROM ({rank_sql.format(src='m_site')}) r
		LEFT JOIN (SELECT DISTINCT ON (account_id) account_id, account_name, account_url
		           FROM all_2022_accounts ORDER BY account_id) a ON a.account_id = r.account_id
		WHERE rn = 1;
		""",
		"""
		CREATE TABLE IF NOT EXISTS domain_account_match (
			source text NOT NULL, domain text NOT NULL, domain_raw text, hacked boolean,
			account_id text NOT NULL, region text, account_name text, account_url text,
			matched_on text, match_tier smallint, n_candidates integer, ambiguous boolean,
			built_at timestamptz DEFAULT now(),
			PRIMARY KEY (source, domain)
		);
		""",
		"DELETE FROM domain_account_match WHERE source = %(source)s;",
		"""
		INSERT INTO domain_account_match
			(source, domain, domain_raw, hacked, account_id, region, account_name, account_url,
			 matched_on, match_tier, n_candidates, ambiguous)
		SELECT %(source)s, x.domain, d.domain_raw, d.hacked, x.account_id, x.region, x.account_name,
		       x.account_url, x.matched_on, x.match_tier, x.n_candidates, x.match_tier IN (3, 6)
		FROM (SELECT * FROM m_by_acc UNION ALL SELECT * FROM m_by_site) x
		JOIN m_dom d USING (domain);
		""",
	]
	summary_sql = """
		SELECT (SELECT COUNT(*) FROM m_dom) AS domains,
		       COUNT(*) AS matched,
		       COUNT(*) FILTER (WHERE matched_on = 'account_url') AS via_account_url,
		       COUNT(*) FILTER (WHERE matched_on = 'site_url')    AS via_site_url,
		       COUNT(*) FILTER (WHERE ambiguous)                  AS ambiguous,
		       COUNT(*) FILTER (WHERE hacked)                     AS hacked
		FROM domain_account_match WHERE source = %(source)s;
	"""
	rows_sql = f"""
		WITH m AS (SELECT * FROM domain_account_match WHERE source = %(source)s),
		     acc AS (
		       SELECT DISTINCT ON (account_id) account_id, account_country, account_state,
		              account_pri_naics6_code, account_employees, account_revenue_usd, account_nb_sites
		       FROM all_2022_accounts
		       WHERE account_id IN (SELECT account_id FROM m)
		       ORDER BY account_id
		     )
		SELECT m.domain, m.domain_raw, m.hacked, m.matched_on, m.match_tier, m.n_candidates, m.ambiguous,
		       m.account_id, m.account_name, m.account_url, m.region,
		       acc.account_country, acc.account_state, acc.account_pri_naics6_code,
		       acc.account_employees, acc.account_revenue_usd, acc.account_nb_sites,
		       COALESCE(nc.n_controls, 0) AS n_controls,
		       x.*
		FROM m
		LEFT JOIN acc USING (account_id)
		LEFT JOIN all_2022_nist_controls nc ON nc.account_id = m.account_id
		LEFT JOIN ({cfg['extras_sql']}) x ON x.domain = m.domain_raw;
	"""
	# One query per regional table: a constant region keeps the scan to that
	# region's sites/technology tables (joining the UNION ALL views on region does not).
	tech_sql = """
		SELECT s.account_id, COUNT(DISTINCT s.site_id) AS num_sites, COUNT(DISTINCT t.product_id) AS n_technologies
		FROM {region}_2022_sites s
		LEFT JOIN {region}_2022_sites_technology t ON t.site_id = s.site_id
		WHERE s.account_id = ANY(%(ids)s)
		GROUP BY 1;
	"""
	phases_sql = """
		SELECT account_id::text AS account_id,
		       COALESCE(NULLIF(nist_phase, 'Multiple'), 'Uncategorized') AS nist_phase
		FROM all_2022_nist_phases
		WHERE account_id::text IN (SELECT account_id FROM domain_account_match WHERE source = %(source)s)
		GROUP BY 1, 2;
	"""

	params = {"source": key, "host_re": HACKED_HOST_RE}
	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			for step in steps:
				cur.execute(step, params)
			conn.commit()
			cur.execute(summary_sql, params)
			summary = dict(zip([d.name for d in cur.description], cur.fetchone()))
			cur.execute(rows_sql, params)
			df = pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
			cur.execute(phases_sql, params)
			phases = pd.DataFrame(cur.fetchall(), columns=["account_id", "nist_phase"])
			# Nested-loop index probes into the 415M-row USA technology table are far
			# slower than one parallel hash join per regional table (~6 min for USA).
			cur.execute("SET enable_nestloop = off;")
			tech_parts = []
			for region in ALL_2022_REGIONS:
				ids = sorted(df.loc[df["region"].fillna("").str.contains(region), "account_id"].dropna().unique().tolist())
				if not ids:
					continue
				cur.execute(tech_sql.format(region=region), {"ids": ids})
				tech_parts.append(pd.DataFrame(cur.fetchall(), columns=["account_id", "num_sites", "n_technologies"]))
	finally:
		conn.close()

	# An account present in several regions gets its sites/technologies summed.
	tech = pd.concat(tech_parts, ignore_index=True) if tech_parts else pd.DataFrame(columns=["account_id", "num_sites", "n_technologies"])
	tech = tech.groupby("account_id", as_index=False).sum() if not tech.empty else tech

	df = df.loc[:, ~df.columns.duplicated()]
	df = df.merge(tech, on="account_id", how="left")
	flags = (
		pd.crosstab(phases["account_id"], phases["nist_phase"]).astype(bool)
		if not phases.empty else pd.DataFrame()
	)
	for phase in NIST_PHASES + ["Uncategorized"]:
		if phase not in flags.columns:
			flags[phase] = False
	flags = flags.rename(columns={p: f"has_{p.lower()}" for p in NIST_PHASES + ["Uncategorized"]}).reset_index()
	if flags.empty:
		flags = pd.DataFrame(columns=["account_id"] + HACKED_PHASE_COLS)
	df = df.merge(flags, on="account_id", how="left")

	NIST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	_hacked_summary_path(key, "accounts").write_text(json.dumps({k: int(v or 0) for k, v in summary.items()}))
	return _hacked_finish_df(df, cfg, "accounts")


_hacked_domain_tech_cache = {}


def _hacked_domain_tech_df(key):
	df = _hacked_domain_tech_cache.get(key)
	if df is None:
		path = _hacked_domain_tech_path(key)
		if not path.exists():
			return None
		df = pd.read_parquet(path)
		_hacked_domain_tech_cache[key] = df
	return df


def _hacked_build_fn(cfg, key, level):
	if level == "domains":
		return lambda: _build_hacked_domains_df(cfg, key)
	if level == "accounts":
		return lambda: _build_hacked_accounts_df(cfg, key)
	return lambda: _build_hacked_sites_df(cfg, key)


def _hacked_get_df(key, level, refresh=False):
	cfg = _hacked_dataset(key)
	_hacked_level(level)
	return _nist_get_df(_hacked_cache_key(key, level), refresh=refresh, build_fn=_hacked_build_fn(cfg, key, level))


def _hacked_stats(df, level):
	"""Cards + NIST coverage (% of rows) for hacked vs not-hacked rows, with
	odds ratios. OR notation: a = Ransomed-Tech, b = Ransomed-NoTech,
	c = NoRansomed-Tech, d = NoRansomed-NoTech."""
	lv = HACKED_LEVELS[level]
	phases = df[lv["phases_col"]]
	n = len(df)
	hacked = df["hacked"].astype(bool)
	n_h = int(hacked.sum())
	n_nh = n - n_h

	metrics = {
		"identify": df["has_identify"],
		"protect": df["has_protect"],
		"detect": df["has_detect"],
		"respond": df["has_respond"],
		"recover": df["has_recover"],
		"uncategorized": df["has_uncategorized"],
		"ge1": phases >= 1,
		"ge2": phases >= 2,
		"ge3": phases >= 3,
		"ge4": phases >= 4,
		"eq5": phases == 5,
	}
	mdf = pd.DataFrame(metrics).astype(int)
	totals = mdf.sum()
	tot_h = mdf[hacked].sum()
	tot_nh = mdf[~hacked].sum()

	def pct(num, den):
		return round(100.0 * num / den, 1) if den else None

	table = {}
	for key in metrics:
		a = int(tot_h[key])
		b = n_h - a
		c = int(tot_nh[key])
		d = n_nh - c
		table[key] = {
			"all": pct(int(totals[key]), n),
			"hacked": pct(a, n_h),
			"not_hacked": pct(c, n_nh),
			"a": a, "b": b, "c": c, "d": d,
			"odds_ratio": round((a * d) / (b * c), 2) if b and c else None,
		}

	sites = int(df[lv["sites_col"]].sum()) if lv["sites_col"] and n else int(n)
	return {
		"rows": int(n),
		"sites": sites,
		"domains": int(df["domain"].nunique()) if n else 0,
		"hacked_rows": n_h,
		"hacked_pct": pct(n_h, n),
		"avg_controls": round(float(df[lv["controls_col"]].mean()), 2) if n else 0,
		"avg_phases": round(float(phases.mean()), 2) if n else 0,
		"denominators": {"all": int(n), "hacked": n_h, "not_hacked": n_nh},
		"table": table,
	}


@app.route("/hacked-sites/<key>", defaults={"level": "sites"})
@app.route("/hacked-sites/<key>/<level>")
def hacked_sites(key, level):
	cfg = _hacked_dataset(key)
	lv = _hacked_level(level)
	column_meta = [{"field": c, "type": t} for c, t in _hacked_columns(cfg, level)]
	return render_template(
		"hacked_sites.html",
		key=key,
		level=level,
		label=cfg["label"],
		level_label=lv["label"],
		column_meta=column_meta,
	)


def _hacked_filtered_df(key, level, args):
	"""Cached df filtered + sorted by request args, or None while building."""
	df = _hacked_get_df(key, level)
	if df is None:
		return None
	num_cols, bool_cols = _hacked_col_sets(HACKED_DATASETS[key], level)
	df = _apply_nist_filters(df, args, num_cols, bool_cols)
	sort = args.get("sort", "")
	direction = args.get("dir", "asc")
	if sort in df.columns:
		df = df.sort_values(sort, ascending=(direction != "desc"), na_position="last", kind="stable")
	return df


@app.route("/api/hacked-sites/<key>/<level>/data")
def hacked_sites_data_api(key, level):
	"""Server-side paginated / filtered / sorted rows plus stats on the filtered set."""
	cache_key = _hacked_cache_key(key, level)
	if request.args.get("refresh") == "1":
		_hacked_get_df(key, level, refresh=True)
		return _nist_building_response(cache_key)
	full = _hacked_get_df(key, level)
	if full is None:
		return _nist_building_response(cache_key)

	try:
		page = max(int(request.args.get("page", 1)), 1)
		size = min(max(int(request.args.get("size", 50)), 1), NIST_MAX_PAGE_SIZE)
	except (TypeError, ValueError):
		return jsonify({"error": "page and size must be numbers."}), 400

	df = _hacked_filtered_df(key, level, request.args)
	stats = _hacked_stats(df, level)
	summary_path = _hacked_summary_path(key, level)
	stats["summary"] = json.loads(summary_path.read_text()) if summary_path.exists() else {}
	total = len(df)
	last_page = max((total + size - 1) // size, 1)
	page = min(page, last_page)
	chunk = df.iloc[(page - 1) * size: page * size]
	rows = chunk.astype(object).where(chunk.notna(), None).to_dict(orient="records")

	return jsonify({
		"data": rows,
		"last_page": last_page,
		"last_row": total,
		"total_all": len(full),
		"stats": stats,
		"built_at": _nist_state(cache_key)["built_at"],
	})


@app.route("/api/hacked-sites/<key>/<level>/download")
def hacked_sites_download(key, level):
	"""CSV of the filtered (and sorted) dataset."""
	df = _hacked_filtered_df(key, level, request.args)
	if df is None:
		return _nist_building_response(_hacked_cache_key(key, level))

	def generate():
		yield df.iloc[0:0].to_csv(index=False)
		for start in range(0, len(df), 50000):
			yield df.iloc[start:start + 50000].to_csv(index=False, header=False)

	return Response(
		generate(),
		mimetype="text/csv",
		headers={"Content-Disposition": f"attachment; filename={key}_hacked_{level}.csv"},
	)


@app.route("/api/hacked-sites/<key>/domain-technologies")
def hacked_domain_technologies_api(key):
	"""JSON API: distinct technologies across all SWDB sites matched to a domain
	(precomputed with the domains dataset)."""
	_hacked_dataset(key)
	domain = request.args.get("domain", "").strip()
	if not domain:
		return jsonify({"error": "domain is required."}), 400
	tech = _hacked_domain_tech_df(key)
	if tech is None:
		return jsonify({"error": "Domain technologies are not built yet; open the Domains page first."}), 409

	df = tech[tech["domain"] == domain].drop(columns=["domain"])
	df = df.sort_values(["security_product", "n_sites", "product"], ascending=[False, False, True])
	security = df[df["security_product"]]
	phase_counts = security["nist_phase"].replace({"": "Uncategorized", "Multiple": "Uncategorized"}).value_counts().to_dict()
	return jsonify({
		"domain": domain,
		"summary": {
			"technologies": int(len(df)),
			"security_products": int(len(security)),
			"nist_phases": len([p for p in phase_counts if p in NIST_PHASES]),
			"phase_counts": {k: int(v) for k, v in phase_counts.items()},
		},
		"rows": df.to_dict(orient="records"),
	})


@app.route("/api/hacked-sites/<key>/site-technologies")
def hacked_site_technologies_api(key):
	"""JSON API: every technology installed at a site, enriched with the NIST
	phase / security category from `universe_installs_enhanced`."""
	_hacked_dataset(key)
	site_id = request.args.get("site_id", "").strip()
	region = request.args.get("region", "").strip()
	if not site_id:
		return jsonify({"error": "site_id is required."}), 400
	# The constant `region` per UNION ALL branch lets PostgreSQL skip the other regional tables.
	region_sql = " AND t.region = %(region)s" if region else ""

	sql = f"""
		SELECT t.product_id,
		       COALESCE(u.vendorname, t.product_vendor)  AS vendor,
		       COALESCE(u.product, t.product)            AS product,
		       u.productcategory,
		       u.actualcat                               AS security_category,
		       CASE WHEN u.security_product
		            THEN COALESCE(NULLIF(u.nist_phase, 'Multiple'), 'Uncategorized')
		       END                                       AS nist_phase,
		       COALESCE(u.security_product, FALSE)       AS security_product,
		       COALESCE(u.is_open_source, FALSE)         AS is_open_source,
		       t.product_confidence_ranking
		FROM all_2022_sites_technology t
		LEFT JOIN universe_installs_enhanced u
		       ON u.productid = NULLIF(t.product_id, '')::int
		WHERE t.site_id = %(site_id)s{region_sql}
		ORDER BY security_product DESC, product;
	"""
	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute(sql, {"site_id": site_id, "region": region})
			rows = [dict(r) for r in cur.fetchall()]
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			try:
				conn.close()
			except Exception:
				pass

	df = pd.DataFrame(rows, columns=[
		"product_id", "vendor", "product", "productcategory", "security_category",
		"nist_phase", "security_product", "is_open_source", "product_confidence_ranking",
	])
	for col in ("vendor", "product", "productcategory", "security_category", "nist_phase"):
		df[col] = df[col].fillna("")

	security = df[df["security_product"] == True]  # noqa: E712 - pandas mask
	phases = {p for p in df["nist_phase"].tolist() if p in NIST_PHASES}
	phase_counts = (
		df.loc[df["nist_phase"] != "", "nist_phase"].value_counts().to_dict()
		if not df.empty else {}
	)
	return jsonify({
		"site_id": site_id,
		"summary": {
			"technologies": int(len(df)),
			"security_products": int(len(security)),
			"nist_phases": len(phases),
			"phase_counts": {k: int(v) for k, v in phase_counts.items()},
		},
		"rows": df.to_dict(orient="records"),
	})



# ---------------------------------------------------------------------------
# Spiceworks (CCID) company browser — swdb_<year>_* tables
# ---------------------------------------------------------------------------

# Each year reads from the summary built by build_swdb_company_summary.py.
SWDB_COMPANY_YEARS = {
	"2023": {
		"label": "2023 · CCID v5.0",
		"summary": "swdb_2023_company_summary",
		"lookup": "swdb_2023_technology_lookup",
		"installs": "swdb_2023_tech_installs",
		"sites": "swdb_2023_site",
	},
}

# (field, type, default visible) — order is the column order in the UI.
# Visible by default: the identification / sizing / location fields requested for the browser.
SWDB_COMPANY_COLUMNS = [
	("company_name", "text", True),
	("company_primary_domain", "text", True),
	("company_website", "text", True),
	("company_domains", "text", True),
	("company_stock_symbol", "text", True),
	("company_start_year", "text", True),
	("company_employees", "num", True),
	("company_annual_revenue", "num", True),
	("company_primary_sic4_description", "text", True),
	("company_location_city", "text", True),
	("company_location_country", "text", True),
	("company_location_type", "text", True),
	("company_location_domestic_hq", "num", True),
	("company_location_legal_status", "text", True),
	("company_location_country_region_code", "text", True),
	("company_type", "text", True),
	("company_public", "num", True),
	("n_technologies", "num", True),
	("n_vendors", "num", True),
	("n_sites", "num", True),
	("company_trade_name", "text", False),
	("company_linkedin_link", "text", False),
	("company_employee_range", "text", False),
	("company_annual_revenue_range", "text", False),
	("company_family_members", "num", False),
	("company_primary_industry", "text", False),
	("company_primary_sub_industry", "text", False),
	("company_location_state", "text", False),
	("company_location_continent", "text", False),
	("company_it_employees", "num", False),
	("company_annual_ict_spending", "num", False),
	("company_annual_ict_spending_range", "text", False),
	("company_servers", "num", False),
	("company_pcs", "num", False),
]
SWDB_COMPANY_FACETS = {
	"company_location_country": "Countries",
	"company_location_country_region_code": "Regions",
	"company_primary_sic4_description": "Industries (SIC4)",
	"company_primary_industry": "Industries",
	"company_location_type": "Location types",
	"company_employee_range": "Employee ranges",
}
SWDB_COMPANY_MAX_PAGE = 500
SWDB_COMPANY_DOWNLOAD_CAP = 500_000
SWDB_COMPANY_CACHE_TTL = 900  # seconds; aggregate queries over millions of rows are cached
_swdb_company_cache = {}
_swdb_company_lock = threading.Lock()
_swdb_summary_columns = {}


def _swdb_row(row):
	"""Convert Decimal/date values from psycopg2 into JSON-friendly numbers/strings."""
	out = {}
	for k, v in row.items():
		if isinstance(v, Decimal):
			out[k] = int(v) if v == v.to_integral_value() else float(v)
		elif v is None or isinstance(v, (bool, int, float, str, list)):
			out[k] = v
		else:
			out[k] = str(v)
	return out


def _swdb_year(year):
	cfg = SWDB_COMPANY_YEARS.get(year)
	if not cfg:
		abort(404)
	return cfg


def _swdb_summary_cols(cfg):
	"""Columns that actually exist in this year's summary (2023 lacks company_type etc.)."""
	table = cfg["summary"]
	with _swdb_company_lock:
		cached = _swdb_summary_columns.get(table)
	if cached is not None:
		return cached
	conn = get_db_connection()
	try:
		with conn.cursor() as cur:
			cur.execute(
				"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s",
				(table,),
			)
			cols = {r[0] for r in cur.fetchall()}
	finally:
		conn.close()
	if cols:
		with _swdb_company_lock:
			_swdb_summary_columns[table] = cols
	return cols


def _swdb_company_column_meta(cfg):
	present = _swdb_summary_cols(cfg)
	return [
		{"field": f, "type": t, "visible": v}
		for f, t, v in SWDB_COMPANY_COLUMNS if f in present
	]


def _swdb_company_where(cfg, args):
	"""Translate f_<column> query params to a parametrised WHERE clause."""
	present = _swdb_summary_cols(cfg)
	clauses, params = [], []
	for field, ftype, _ in SWDB_COMPANY_COLUMNS:
		if field not in present:
			continue
		raw = (args.get(f"f_{field}") or "").strip()
		if not raw:
			continue
		if ftype == "num":
			m = _NUM_FILTER_RE.match(raw)
			if not m:
				continue
			op = m.group(1) or "="
			clauses.append(f"{field} {op} %s")
			params.append(float(m.group(2)))
		elif raw.startswith("="):
			# IN-list keeps the btree index usable while tolerating common casings.
			clauses.append(f"{field} IN (%s, initcap(%s), upper(%s), lower(%s))")
			params.extend([raw[1:]] * 4)
		else:
			clauses.append(f"{field} ILIKE %s")
			params.append("%" + raw.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%")
	where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
	return where, params


def _swdb_cached(key, compute):
	now = datetime.now().timestamp()
	with _swdb_company_lock:
		hit = _swdb_company_cache.get(key)
		if hit and now - hit[0] < SWDB_COMPANY_CACHE_TTL:
			return hit[1]
	value = compute()
	with _swdb_company_lock:
		if len(_swdb_company_cache) > 300:
			_swdb_company_cache.clear()
		_swdb_company_cache[key] = (now, value)
	return value


def _swdb_summary_missing(cfg):
	return not _swdb_summary_cols(cfg)


@app.route("/swdb-companies/<year>")
def swdb_companies(year):
	cfg = _swdb_year(year)
	return render_template(
		"swdb_companies.html",
		year=year,
		year_label=cfg["label"],
		years=[{"key": k, "label": v["label"]} for k, v in SWDB_COMPANY_YEARS.items()],
		column_meta=_swdb_company_column_meta(cfg),
		facets=SWDB_COMPANY_FACETS,
		download_cap=SWDB_COMPANY_DOWNLOAD_CAP,
	)


SWDB_STATS_TABLE = "swdb_company_summary_stats"
SWDB_STATS_SAMPLE_ABOVE = 1_000_000  # medians over bigger filtered sets are estimated on a sample
SWDB_STATS_SQL = """
	SELECT count(*)                                            AS companies,
	       COALESCE(sum(n_technologies), 0)                    AS tech_installs,
	       COALESCE(avg(n_technologies), 0)                    AS avg_tech,
	       count(DISTINCT company_location_country)            AS countries,
	       count(DISTINCT company_primary_sic4_description)    AS industries,
	       COALESCE(sum(n_sites), 0)                           AS sites,
	       count(company_employees)                            AS with_employees
	FROM {table}{where}
"""
SWDB_MEDIAN_SQL = """
	SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY n_technologies)   AS median_tech,
	       percentile_cont(0.5) WITHIN GROUP (ORDER BY company_employees) AS median_employees
	FROM {table}{sample}{where}
"""


SWDB_FILTER_FIRST_BELOW = 2_000_000


def _swdb_order(fields, args, filter_first=False):
	"""ORDER BY clause for the companies list.

	NULLS placement mirrors the indexes (numeric: DESC NULLS LAST, text: ASC NULLS LAST)
	so both scan directions stay index-backed on the 18M-row summary. With
	``filter_first`` the sort key is wrapped in an expression: that stops the
	planner from walking the sort index hoping to hit LIMIT rows (very slow when
	the filter is selective) and makes it filter via the other indexes first.
	"""
	sort = args.get("sort", "")
	direction = "DESC" if args.get("dir", "asc") == "desc" else "ASC"
	if sort not in fields:
		sort, direction = "n_technologies", "DESC"
	is_num = any(f == sort and t == "num" for f, t, _ in SWDB_COMPANY_COLUMNS)
	natural = "DESC" if is_num else "ASC"
	nulls = "NULLS LAST" if direction == natural else "NULLS FIRST"
	key = sort
	if filter_first:
		key = f"({sort} + 0)" if is_num else f"({sort} || '')"
	return f" ORDER BY {key} {direction} {nulls}, company_id"


def _swdb_global_stats(cfg, year):
	"""Whole-dataset aggregates stored by build_swdb_company_summary.py (None if missing)."""
	def compute():
		conn = get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{SWDB_STATS_TABLE}",))
				if not cur.fetchone()[0]:
					return None
				cur.execute(f"SELECT stats, computed_at FROM {SWDB_STATS_TABLE} WHERE year = %s", (year,))
				row = cur.fetchone()
				if not row:
					return None
				stats = dict(row[0])
				stats["computed_at"] = row[1].isoformat()
				stats["exact_medians"] = True
				return stats
		finally:
			conn.close()
	return _swdb_cached(("global", year), compute)


def _swdb_count(cfg, year, where, params):
	"""Row count for a filter set (cached; the unfiltered count comes from the stored stats)."""
	if not where:
		g = _swdb_global_stats(cfg, year)
		if g:
			return int(g["companies"])

	def compute():
		conn = get_db_connection()
		try:
			with conn.cursor() as cur:
				cur.execute("SET statement_timeout = 120000")
				cur.execute(f"SELECT count(*) FROM {cfg['summary']}{where}", params)
				return int(cur.fetchone()[0])
		finally:
			conn.close()
	return _swdb_cached(("count", year, where, tuple(params)), compute)


@app.route("/api/swdb-companies/<year>/data")
def swdb_companies_data_api(year):
	"""Server-side paginated / filtered / sorted companies (stats come from /stats)."""
	cfg = _swdb_year(year)
	if _swdb_summary_missing(cfg):
		return jsonify({"error": f"Summary table {cfg['summary']} not found. Run build_swdb_company_summary.py {year}."}), 503

	try:
		page = max(int(request.args.get("page", 1)), 1)
		size = min(max(int(request.args.get("size", 50)), 1), SWDB_COMPANY_MAX_PAGE)
	except (TypeError, ValueError):
		return jsonify({"error": "page and size must be numbers."}), 400

	present = _swdb_summary_cols(cfg)
	fields = [f for f, _, _ in SWDB_COMPANY_COLUMNS if f in present]
	where, params = _swdb_company_where(cfg, request.args)

	conn = None
	try:
		total = _swdb_count(cfg, year, where, params)
		rows = []
		if total and (page - 1) * size < total:
			order = _swdb_order(fields, request.args, filter_first=bool(where) and total < SWDB_FILTER_FIRST_BELOW)
			select_sql = f"SELECT company_id, {', '.join(fields)} FROM {cfg['summary']}{where}{order} LIMIT %s OFFSET %s"
			conn = get_db_connection()
			conn.set_session(readonly=True)
			with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
				cur.execute("SET statement_timeout = 120000")
				cur.execute(select_sql, params + [size, (page - 1) * size])
				rows = [_swdb_row(dict(r)) for r in cur.fetchall()]
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			conn.close()

	return jsonify({
		"data": rows,
		"last_page": max((total + size - 1) // size, 1),
		"last_row": total,
	})


@app.route("/api/swdb-companies/<year>/stats")
def swdb_companies_stats_api(year):
	"""Aggregate cards for the filtered set. Unfiltered → stored global stats; large sets → sampled medians."""
	cfg = _swdb_year(year)
	if _swdb_summary_missing(cfg):
		return jsonify({"error": "Summary table not found."}), 503
	where, params = _swdb_company_where(cfg, request.args)

	if not where:
		g = _swdb_global_stats(cfg, year)
		if g:
			return jsonify({"stats": g})

	def compute():
		total = _swdb_count(cfg, year, where, params)
		sampled = total > SWDB_STATS_SAMPLE_ABOVE
		sample = " TABLESAMPLE SYSTEM (2)" if sampled else ""
		conn = get_db_connection()
		try:
			with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
				cur.execute("SET statement_timeout = 180000")
				cur.execute(SWDB_STATS_SQL.format(table=cfg["summary"], where=where), params)
				stats = _swdb_row(dict(cur.fetchone()))
				cur.execute(SWDB_MEDIAN_SQL.format(table=cfg["summary"], sample=sample, where=where), params)
				stats.update(_swdb_row(dict(cur.fetchone())))
				stats["exact_medians"] = not sampled
				return stats
		finally:
			conn.close()

	try:
		stats = _swdb_cached(("stats", year, where, tuple(params)), compute)
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	return jsonify({"stats": stats})


@app.route("/api/swdb-companies/<year>/facet")
def swdb_companies_facet_api(year):
	"""Distinct values + counts of one categorical column within the filtered set."""
	cfg = _swdb_year(year)
	field = request.args.get("field", "")
	if field not in SWDB_COMPANY_FACETS or field not in _swdb_summary_cols(cfg):
		return jsonify({"error": "Unknown facet field."}), 400
	where, params = _swdb_company_where(cfg, request.args)
	sql = f"""
		SELECT COALESCE({field}, '(blank)') AS value, count(*) AS companies,
		       sum(n_technologies) AS tech_installs, avg(n_technologies) AS avg_tech
		FROM {cfg['summary']}{where}
		GROUP BY 1 ORDER BY companies DESC LIMIT 2000
	"""

	def compute():
		conn = get_db_connection()
		try:
			with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
				cur.execute("SET statement_timeout = 120000")
				cur.execute(sql, params)
				return [_swdb_row(dict(r)) for r in cur.fetchall()]
		finally:
			conn.close()

	try:
		rows = _swdb_cached(("facet", year, field, where, tuple(params)), compute)
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	return jsonify({"field": field, "label": SWDB_COMPANY_FACETS[field], "rows": rows})


@app.route("/api/swdb-companies/<year>/company")
def swdb_company_detail_api(year):
	"""Company profile (every summary column) plus its detected technologies."""
	cfg = _swdb_year(year)
	company_id = request.args.get("company_id", "").strip()
	if not company_id:
		return jsonify({"error": "company_id is required."}), 400

	tech_sql = f"""
		SELECT l.tech_id::int AS tech_id, l.tech_vendor, l.tech_name, l.tech_category, l.tech_series,
		       l.tech_hosting, l.tech_url, l.tech_vendor_url, i.n_installs
		FROM {cfg['summary']} s
		CROSS JOIN LATERAL unnest(s.tech_ids) AS u(tech_id)
		JOIN {cfg['lookup']} l ON l.tech_id::int = u.tech_id
		LEFT JOIN {cfg['installs']} i ON i.tech_id = l.tech_id
		WHERE s.company_id = %s
		ORDER BY i.n_installs DESC NULLS LAST, l.tech_name
	"""
	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute("SET statement_timeout = 60000")
			cur.execute(f"SELECT * FROM {cfg['summary']} WHERE company_id = %s", (company_id,))
			company = cur.fetchone()
			if not company:
				return jsonify({"error": "Company not found."}), 404
			company = dict(company)
			company.pop("tech_ids", None)
			cur.execute(tech_sql, (company_id,))
			techs = [dict(r) for r in cur.fetchall()]
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			conn.close()

	techs = [_swdb_row(r) for r in techs]
	company = _swdb_row(company)
	categories = {}
	for r in techs:
		categories[r["tech_category"] or "(none)"] = categories.get(r["tech_category"] or "(none)", 0) + 1
	return jsonify({
		"company": company,
		"technologies": techs,
		"summary": {
			"technologies": len(techs),
			"vendors": len({r["tech_vendor"] for r in techs if r["tech_vendor"]}),
			"categories": sorted(categories.items(), key=lambda kv: -kv[1]),
		},
	})


@app.route("/api/swdb-companies/<year>/sites")
def swdb_company_sites_api(year):
	"""Every site (all columns) belonging to a company, largest first."""
	cfg = _swdb_year(year)
	company_id = request.args.get("company_id", "").strip()
	if not company_id:
		return jsonify({"error": "company_id is required."}), 400
	if not cfg.get("sites"):
		return jsonify({"error": "No site table for this year."}), 404

	sql = f"""
		SELECT * FROM {cfg['sites']}
		WHERE company_id = %s
		ORDER BY CASE WHEN site_employees ~ '^[0-9]+$' THEN site_employees::bigint END DESC NULLS LAST, site_name
		LIMIT 20000
	"""
	conn = None
	try:
		conn = get_db_connection()
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute("SET statement_timeout = 60000")
			cur.execute(sql, (company_id,))
			rows = [_swdb_row(dict(r)) for r in cur.fetchall()]
			columns = [d.name for d in cur.description]
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			conn.close()

	for r in rows:
		r.pop("company_id", None)
		for k in ("site_employees", "site_domestic_hq"):
			v = r.get(k)
			if isinstance(v, str) and v.lstrip("-").isdigit():
				r[k] = int(v)
	columns = [c for c in columns if c != "company_id"]
	return jsonify({"company_id": company_id, "columns": columns, "rows": rows, "truncated": len(rows) >= 20000})


# ---- Company search (form-based) ----

# (field, kind, options) — kind: text | int | enum
SWDB_SEARCH_FIELDS = [
	("company_name", "text", None),
	("company_primary_domain", "text", None),
	("company_website", "text", None),
	("company_domains", "text", None),
	("company_stock_symbol", "text", None),
	("company_start_year", "text", None),
	("company_employees", "int", None),
	("company_annual_revenue", "int", None),
	("company_primary_sic4_description", "text", None),
	("company_location_city", "text", None),
	("company_location_country", "text", None),
	("company_location_type", "enum", ["BRA", "SLS", "SHQ", "STA", "UHQ"]),
	("company_location_domestic_hq", "enum", ["0", "1"]),
	("company_location_legal_status", "text", None),
	("company_location_country_region_code", "enum", ["Ant", "APac", "EMEA", "LatAm", "NA"]),
	("company_type", "enum", ["ST", "SU", "UP"]),
	("company_public", "enum", ["0", "1"]),
]
SWDB_SEARCH_RESULT_EXTRA = ["n_technologies", "n_vendors", "n_sites"]
SWDB_SEARCH_MAX_ROWS = 1000
SWDB_SEARCH_COUNT_CAP = 10000


def _swdb_search_where(cfg, args):
	"""WHERE clause from the search form: text contains/exact, numeric min/max, enum equality."""
	present = _swdb_summary_cols(cfg)
	exact = args.get("exact") == "1"
	clauses, params = [], []
	for field, kind, _ in SWDB_SEARCH_FIELDS:
		if field not in present:
			continue
		if kind == "int":
			for suffix, op in (("_min", ">="), ("_max", "<=")):
				raw = (args.get(field + suffix) or "").replace(",", "").strip()
				if raw:
					try:
						params.append(float(raw))
					except ValueError:
						continue
					clauses.append(f"{field} {op} %s")
			continue
		raw = (args.get(field) or "").strip()
		if not raw:
			continue
		if kind == "enum":
			clauses.append(f"{field} = %s")
			params.append(raw)
		elif exact:
			clauses.append(f"{field} IN (%s, initcap(%s), upper(%s), lower(%s))")
			params.extend([raw] * 4)
		else:
			esc = raw.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
			clauses.append(f"{field} ILIKE %s")
			params.append("%" + esc + "%")
	return (" WHERE " + " AND ".join(clauses)) if clauses else "", params


@app.route("/swdb-companies/<year>/search")
def swdb_company_search(year):
	cfg = _swdb_year(year)
	present = _swdb_summary_cols(cfg)
	fields = [{"field": f, "kind": k, "options": o, "available": f in present} for f, k, o in SWDB_SEARCH_FIELDS]
	return render_template(
		"swdb_company_search.html",
		year=year, year_label=cfg["label"],
		years=[{"key": k, "label": v["label"]} for k, v in SWDB_COMPANY_YEARS.items()],
		fields=fields, max_rows=SWDB_SEARCH_MAX_ROWS,
	)


@app.route("/api/swdb-companies/<year>/search")
def swdb_company_search_api(year):
	"""Companies matching the form criteria (max SWDB_SEARCH_MAX_ROWS, most technologies first)."""
	cfg = _swdb_year(year)
	if _swdb_summary_missing(cfg):
		return jsonify({"error": f"Summary table {cfg['summary']} not found."}), 503
	where, params = _swdb_search_where(cfg, request.args)
	if not where:
		return jsonify({"error": "Enter at least one search criterion."}), 400

	present = _swdb_summary_cols(cfg)
	fields = [f for f, _, _ in SWDB_SEARCH_FIELDS if f in present] + SWDB_SEARCH_RESULT_EXTRA
	try:
		limit = min(max(int(request.args.get("limit", SWDB_SEARCH_MAX_ROWS)), 1), SWDB_SEARCH_MAX_ROWS)
	except (TypeError, ValueError):
		limit = SWDB_SEARCH_MAX_ROWS

	rows_sql = (f"SELECT company_id, {', '.join(fields)} FROM {cfg['summary']}{where} "
				f"ORDER BY (n_technologies + 0) DESC, company_id LIMIT %s")
	# Bounded count: scanning past the cap would make broad searches slow.
	count_sql = f"SELECT count(*) FROM (SELECT 1 FROM {cfg['summary']}{where} LIMIT %s) t"

	conn = None
	started = datetime.now()
	try:
		conn = get_db_connection()
		conn.set_session(readonly=True)
		with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute("SET statement_timeout = 120000")
			cur.execute(rows_sql, params + [limit])
			rows = [_swdb_row(dict(r)) for r in cur.fetchall()]
			total = len(rows)
			capped = False
			if total >= limit:
				cur.execute(count_sql, params + [SWDB_SEARCH_COUNT_CAP + 1])
				total = int(cur.fetchone()["count"])
				capped = total > SWDB_SEARCH_COUNT_CAP
				if capped:
					total = SWDB_SEARCH_COUNT_CAP
	except psycopg2.errors.QueryCanceled:
		return jsonify({"error": "The search took too long (>120 s). Add more specific criteria."}), 504
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500
	finally:
		if conn:
			conn.close()

	return jsonify({
		"rows": rows, "columns": fields, "returned": len(rows), "total": total,
		"total_capped": capped, "limit": limit,
		"elapsed_ms": int((datetime.now() - started).total_seconds() * 1000),
	})


@app.route("/api/swdb-companies/<year>/download")
def swdb_companies_download(year):
	"""CSV of the filtered (and sorted) companies, capped at SWDB_COMPANY_DOWNLOAD_CAP rows."""
	cfg = _swdb_year(year)
	present = _swdb_summary_cols(cfg)
	fields = [f for f, _, _ in SWDB_COMPANY_COLUMNS if f in present]
	where, params = _swdb_company_where(cfg, request.args)
	sql = (f"SELECT company_id, {', '.join(fields)} FROM {cfg['summary']}{where}"
		   f"{_swdb_order(fields, request.args, filter_first=bool(where))} LIMIT {SWDB_COMPANY_DOWNLOAD_CAP}")

	def generate():
		conn = get_db_connection()
		try:
			with conn.cursor(name="swdb_companies_dl") as cur:
				cur.itersize = 20000
				cur.execute(sql, params)
				buf = io.StringIO()
				writer = csv.writer(buf)
				writer.writerow(["company_id"] + fields)
				yield buf.getvalue()
				for chunk in iter(lambda: cur.fetchmany(20000), []):
					buf = io.StringIO()
					writer = csv.writer(buf)
					writer.writerows(chunk)
					yield buf.getvalue()
		finally:
			conn.close()

	return Response(
		generate(),
		mimetype="text/csv",
		headers={"Content-Disposition": f"attachment; filename=swdb_{year}_companies.csv"},
	)


if __name__ == "__main__":
	# ip to run the app: 127.0.0.1 and 10.20.5.20 on port 80 both
	app.run(host="0.0.0.0", port=8888)