from flask import Flask, render_template, request, jsonify
import markdown
from pathlib import Path
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

				if where_sql:
					query = f"SELECT * FROM {table} WHERE {where_sql} LIMIT 500;"
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


if __name__ == "__main__":
	# ip to run the app: 127.0.0.1 and 10.20.5.20 on port 80 both
	app.run(host="0.0.0.0", port=8888)