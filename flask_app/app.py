from flask import Flask, render_template, request, jsonify, abort
import markdown
from pathlib import Path
import csv
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
	)


@app.route("/")
def index():
	# Default example query; user can overwrite it in the UI
	example_query = "SELECT * FROM usa_2015_hist2015_sitedesc LIMIT 100;"
	return render_template("index.html", example_query=example_query)


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
	"""Render the SWDB schema page."""
	return render_template("swdb_schema.html")


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
		"title": "Universe Installs",
		"template": "general_info.html",
		"dedupe": True,
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
}


def _load_general_info_df(filename, dedupe=False):
	"""Load a general-info CSV with pandas and normalise it.

	- Reads everything as strings first (so IDs / codes are preserved).
	- Drops fully empty/unnamed columns.
	- Optionally removes duplicate rows.
	- Detects numeric columns (including values formatted like "696,761")
	  and converts them, returning the list of numeric column names.
	"""

	csv_path = Path(__file__).parent / "data" / "swdb_general_info" / filename
	df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

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
		"datasets": GENERAL_INFO_DATASETS,
	}

	# Pretty, server-rendered presentation pages get their data up-front.
	if template != "general_info.html":
		try:
			df, numeric_cols = _load_general_info_df(
				dataset["file"], dedupe=dataset.get("dedupe", False)
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
			dataset["file"], dedupe=dataset.get("dedupe", False)
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


if __name__ == "__main__":
	# ip to run the app: 127.0.0.1 and 10.20.5.20 on port 80 both
	app.run(host="0.0.0.0", port=8888)