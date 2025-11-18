from flask import Flask, render_template, request, jsonify
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
	)


@app.route("/")
def index():
	# Default example query; user can overwrite it in the UI
	example_query = "SELECT * FROM usa_2009_hist2009_system LIMIT 100;"
	return render_template("index.html", example_query=example_query)


@app.route("/companies")
def companies():
	"""Companies search page.

	Allows searching by company name, year bucket, and optional region.
	
	Year buckets map to different underlying tables/columns as provided:
	- 2000/2009: usa_2009_hist2009_sitedesc.company
	- 2010-2015: usa_2015_hist2015_sitedesc.company
	- 2016-2020: usa_2016_sitedescription.company
	- 2020-2022: usa_2022_sites.site_name
	"""

	company_name = request.args.get("company", "").strip()
	year_raw = request.args.get("year")

	rows = []
	columns = []
	error = None
	company_searched = bool(company_name)
	selected_year = None

	if company_name and year_raw:
		# Parse chosen year
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
				# 2010-2015: usa_[year]_hist[year]_sitedesc, company column
				table = f"usa_{year}_hist{year}_sitedesc"
				company_col = "company"
			elif 2016 <= year <= 2020:
				# 2016-2020: usa_[year]_sitedescription, company column
				table = f"usa_{year}_site_description"
				company_col = "company"
			elif 2020 <= year <= 2022:
				# 2020-2022: usa_[year]_sites, site_name column
				table = f"usa_{year}_sites"
				company_col = "site_name"
			else:
				error = "Year must be between 2000 and 2022."

			if not error:
				# Build parameterised query to avoid SQL injection
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
		"companies.html",
		rows=rows,
		columns=columns,
		error=error,
		company_searched=company_searched,
		selected_year=selected_year,
	)


@app.route("/api/company-search")
def company_search_api():
	"""JSON API: search companies by name and year, reusing the companies mapping.

	Expected query parameters:
	- company: partial company name (required)
	- year: integer year between 2000 and 2022 (required)

	Returns JSON with keys:
	- columns: list of column names
	- rows: list of row objects (as dictionaries)
	- error: optional error message
	"""

	company_name = request.args.get("company", "").strip()
	year_raw = request.args.get("year")

	if not company_name or not year_raw:
		return jsonify({"error": "Both company and year are required."}), 400

	rows = []
	columns = []
	try:
		year = int(year_raw)
	except (TypeError, ValueError):
		return jsonify({"error": "Year must be a valid number."}), 400

	# Choose table and column pattern based on year (same logic as /companies)
	if year in (2000, 2009):
		# 2000 & 2009: usa_[year]_hist[year]_sitedesc, company column
		table = f"usa_{year}_hist{year}_sitedesc"
		company_col = "company"
	elif 2010 <= year <= 2015:
		# 2010-2015: usa_[year]_hist[year]_sitedesc, company column
		table = f"usa_{year}_hist{year}_sitedesc"
		company_col = "company"
	elif 2016 <= year <= 2020:
		# 2016-2020: usa_[year]_site_description, company column
		table = f"usa_{year}_site_description"
		company_col = "company"
	elif 2020 <= year <= 2022:
		# 2020-2022: usa_[year]_sites, site_name column
		table = f"usa_{year}_sites"
		company_col = "site_name"
	else:
		return jsonify({"error": "Year must be between 2000 and 2022."}), 400

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


@app.route("/api/query", methods=["POST"])
def run_query():
	"""Run an ad‑hoc SQL query and return results as JSON.

	This is intentionally minimal for an internal academic tool. It assumes
	trusted users; do not expose as‑is to the open internet.
	"""

	sql = (request.json or {}).get("sql")
	if not sql or not isinstance(sql, str):
		return jsonify({"error": "No SQL query provided."}), 400

	# Simple guardrails: only allow SELECT queries
	if not sql.strip().lower().startswith("select"):
		return jsonify({"error": "Only SELECT queries are allowed."}), 400

	try:
		conn = get_db_connection()
		with conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
			cur.execute(sql)
			rows = cur.fetchall()
			columns = [desc.name for desc in cur.description] if cur.description else []
	except Exception as exc:  # pragma: no cover - simple error surface
		return jsonify({"error": str(exc)}), 400
	finally:
		try:
			conn.close()
		except Exception:
			pass

	return jsonify({
		"columns": columns,
		"rows": rows,
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

	def resolve_table_and_id(year: int):
		if year in (2000, 2009):
			return f"usa_{year}_hist{year}_sitedesc", "siteid"
		elif 2010 <= year <= 2015:
			return f"usa_{year}_hist{year}_model", "siteid"
		elif 2016 <= year <= 2020:
			return f"usa_{year}_product_install", "siteid"
		elif 2020 <= year <= 2022:
			return f"usa_{year}_sites_technology", "site_id"
		return None, None

	# Base query
	if siteid and year_raw:
		try:
			year = int(year_raw)
		except (TypeError, ValueError):
			error = "Base year must be a valid number."
		else:
			selected_year = year
			table, id_col = resolve_table_and_id(year)
			if not table:
				error = "Base year must be between 2000 and 2022."
			else:
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

	# Comparison query
	if not error and comp_siteid and comp_year_raw:
		try:
			comp_year = int(comp_year_raw)
		except (TypeError, ValueError):
			error = "Comparison year must be a valid number."
		else:
			comp_selected_year = comp_year
			comp_table, comp_id_col = resolve_table_and_id(comp_year)
			if not comp_table:
				error = "Comparison year must be between 2000 and 2022."
			else:
				where_sql = f"{comp_id_col} = %s"
				params = [comp_siteid]
				query = f"SELECT * FROM {comp_table} WHERE {where_sql} LIMIT 500;"
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


if __name__ == "__main__":
	# ip to run the app: 127.0.0.1 and 10.20.5.20 on port 80 both
	app.run(host="0.0.0.0", port=8888)