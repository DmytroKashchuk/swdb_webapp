"""Build the per-year company summary table used by the Spiceworks company browser.

    python build_swdb_company_summary.py 2023 [--drop] [--stats-only] [--add-columns]

Creates ``swdb_<year>_company_summary`` (one row per company with >= 1 detected
technology) from the raw ``swdb_<year>_*`` tables, with firmographics, tech
sizing, site count and an int[] of tech_ids, then indexes it. The raw
technology table has 200M+ rows and no indexes, so this is a one-off batch job
(expect 10-40 minutes); the web app only ever reads the summary.

Global aggregates (counts, medians, ...) over the whole summary are too slow to
compute per request, so they are stored in ``swdb_company_summary_stats``
(one JSON row per year). ``--stats-only`` refreshes just that row.

``--add-columns`` backfills summary columns that were added to COMPANY_COLUMNS /
SIZING_COLUMNS after the summary was built (joins the raw company table once,
no technology scan) and (re)creates any missing indexes - much faster than --drop.
"""
import argparse
import sys
import time
from datetime import datetime

import json

import psycopg2

from app import get_db_connection

# (column, cast) - cast "int"/"numeric" uses a regex guard so dirty values become NULL.
COMPANY_COLUMNS = [
	("company_name", None), ("company_trade_name", None), ("company_primary_domain", None),
	("company_website", None), ("company_domains", None), ("company_linkedin_link", None), ("company_stock_symbol", None),
	("company_start_year", None), ("company_employees", "int"), ("company_employee_range", None),
	("company_annual_revenue", "numeric"), ("company_annual_revenue_range", None),
	("company_family_members", "int"), ("company_primary_sic4_code", None),
	("company_primary_sic4_description", None), ("company_primary_naics6_description", None),
	("company_primary_industry", None), ("company_primary_sub_industry", None),
	("company_location_city", None), ("company_location_state", None),
	("company_location_country", None), ("company_location_country_code", None),
	("company_location_country_region_code", None), ("company_location_continent", None),
	("company_location_type", None), ("company_location_domestic_hq", "int"),
	("company_location_legal_status", None),
	# v5.1+ only
	("company_type", None), ("company_public", "int"),
]
SIZING_COLUMNS = [
	("company_it_employees", "int"), ("company_it_employee_range", None),
	("company_annual_ict_spending", "numeric"), ("company_annual_ict_spending_range", None),
	("company_annual_hw_spending", "numeric"), ("company_annual_sw_spending", "numeric"),
	("company_annual_it_comnet_spending", "numeric"), ("company_annual_it_services_spending", "numeric"),
	("company_annual_it_staff_spending", "numeric"), ("company_annual_telco_spending", "numeric"),
	("company_servers", "int"), ("company_workstations", "int"), ("company_pcs", "int"),
	("company_desktops", "int"), ("company_laptops", "int"), ("company_tablets", "int"),
	("company_printers", "int"), ("company_storage", "int"),
]


def log(msg):
	print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def existing_columns(cur, table):
	cur.execute(
		"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s",
		(table,),
	)
	return {r[0] for r in cur.fetchall()}


def cast_expr(alias, col, cast):
	ref = f"{alias}.{col}"
	if cast == "int":
		return f"CASE WHEN {ref} ~ '^-?[0-9]+$' THEN {ref}::bigint END AS {col}"
	if cast == "numeric":
		return f"CASE WHEN {ref} ~ '^-?[0-9]+(\\.[0-9]+)?$' THEN {ref}::numeric END AS {col}"
	return f"NULLIF({ref}, '') AS {col}"


def table_exists(cur, table):
	cur.execute("SELECT to_regclass(%s) IS NOT NULL", (f"public.{table}",))
	return cur.fetchone()[0]


def build(year, drop):
	t_company = f"swdb_{year}_company"
	t_tech = f"swdb_{year}_company_technology"
	t_sizing = f"swdb_{year}_company_tech_sizing"
	t_site = f"swdb_{year}_site"
	t_summary = f"swdb_{year}_company_summary"

	conn = get_db_connection()
	conn.autocommit = True
	cur = conn.cursor()
	cur.execute("SET statement_timeout = 0")
	cur.execute("SET work_mem = '2GB'")
	cur.execute("SET maintenance_work_mem = '4GB'")

	for t in (t_company, t_tech):
		if not table_exists(cur, t):
			sys.exit(f"Required table {t} does not exist.")
	if table_exists(cur, t_summary):
		if not drop:
			sys.exit(f"{t_summary} already exists; pass --drop to rebuild.")
		log(f"Dropping {t_summary}")
		cur.execute(f"DROP TABLE {t_summary}")

	company_cols = existing_columns(cur, t_company)
	sizing_cols = existing_columns(cur, t_sizing) if table_exists(cur, t_sizing) else set()
	has_sites = table_exists(cur, t_site)
	tech_cols = existing_columns(cur, t_tech)

	select_company = [cast_expr("c", col, cast) for col, cast in COMPANY_COLUMNS if col in company_cols]
	select_sizing = [cast_expr("s", col, cast) for col, cast in SIZING_COLUMNS if col in sizing_cols]
	skipped = [c for c, _ in COMPANY_COLUMNS if c not in company_cols]
	if skipped:
		log(f"Columns not present in {t_company} (skipped): {', '.join(skipped)}")

	tech_extra = ""
	if "tech_confidence_score" in tech_cols:
		tech_extra = ",\n\t\t\t   avg(CASE WHEN tech_confidence_score ~ '^[0-9.]+$' THEN tech_confidence_score::numeric END)::numeric(5,1) AS avg_tech_confidence"

	sizing_join = f"LEFT JOIN {t_sizing} s ON s.company_id = t.company_id" if sizing_cols else ""
	sites_cte = f""",
	sites AS (
		SELECT company_id, count(*)::int AS n_sites FROM {t_site} GROUP BY company_id
	)""" if has_sites else ""
	sites_join = "LEFT JOIN sites si ON si.company_id = t.company_id" if has_sites else ""
	sites_sel = "COALESCE(si.n_sites, 0) AS n_sites," if has_sites else "NULL::int AS n_sites,"

	sql = f"""
	CREATE TABLE {t_summary} AS
	WITH tech AS (
		SELECT company_id,
			   count(*)::int AS n_technologies,
			   count(DISTINCT tech_vendor)::int AS n_vendors,
			   array_agg(tech_id::int ORDER BY tech_id::int) AS tech_ids{tech_extra}
		FROM {t_tech}
		WHERE company_id IS NOT NULL AND tech_id ~ '^[0-9]+$'
		GROUP BY company_id
	){sites_cte}
	SELECT t.company_id,
		   {', '.join(select_company)},
		   {(', '.join(select_sizing) + ',') if select_sizing else ''}
		   {sites_sel}
		   t.n_technologies, t.n_vendors, t.tech_ids{', t.avg_tech_confidence' if tech_extra else ''}
	FROM tech t
	JOIN {t_company} c ON c.company_id = t.company_id
	{sizing_join}
	{sites_join};
	"""

	log(f"Building {t_summary} (this scans {t_tech}; expect a long wait)…")
	t0 = time.time()
	cur.execute(sql)
	log(f"Table created in {(time.time() - t0) / 60:.1f} min")

	create_indexes(cur, year, has_sites)

	cur.execute(f"ANALYZE {t_summary}")
	cur.execute(f"SELECT count(*), pg_size_pretty(pg_total_relation_size('{t_summary}')) FROM {t_summary}")
	n, size = cur.fetchone()
	log(f"Done: {t_summary} has {n:,} companies, {size} on disk")
	compute_global_stats(cur, year)
	conn.close()


def summary_indexes(t_summary):
	return [
		f"CREATE UNIQUE INDEX {t_summary}_pk ON {t_summary} (company_id)",
		# "DESC NULLS LAST" matches the ORDER BY the app emits (and ASC NULLS FIRST when scanned backwards).
		f"CREATE INDEX {t_summary}_ntech ON {t_summary} (n_technologies DESC NULLS LAST, company_id)",
		f"CREATE INDEX {t_summary}_nvend ON {t_summary} (n_vendors DESC NULLS LAST, company_id)",
		f"CREATE INDEX {t_summary}_nsites ON {t_summary} (n_sites DESC NULLS LAST, company_id)",
		f"CREATE INDEX {t_summary}_emp ON {t_summary} (company_employees DESC NULLS LAST, company_id)",
		f"CREATE INDEX {t_summary}_rev ON {t_summary} (company_annual_revenue DESC NULLS LAST, company_id)",
		f"CREATE INDEX {t_summary}_name ON {t_summary} (company_name ASC NULLS LAST, company_id)",
		f"CREATE INDEX {t_summary}_country ON {t_summary} (company_location_country)",
		f"CREATE INDEX {t_summary}_sic4 ON {t_summary} (company_primary_sic4_description)",
		f"CREATE INDEX {t_summary}_sic4_trgm ON {t_summary} USING gin (company_primary_sic4_description gin_trgm_ops)",
		f"CREATE INDEX {t_summary}_name_trgm ON {t_summary} USING gin (company_name gin_trgm_ops)",
		f"CREATE INDEX {t_summary}_domain_trgm ON {t_summary} USING gin (company_primary_domain gin_trgm_ops)",
		f"CREATE INDEX {t_summary}_tech_ids ON {t_summary} USING gin (tech_ids)",
		# Search-form fields
		f"CREATE INDEX {t_summary}_emp_asc ON {t_summary} (company_employees) WHERE company_employees IS NOT NULL",
		f"CREATE INDEX {t_summary}_rev_asc ON {t_summary} (company_annual_revenue) WHERE company_annual_revenue IS NOT NULL",
		f"CREATE INDEX {t_summary}_loctype ON {t_summary} (company_location_type)",
		f"CREATE INDEX {t_summary}_region ON {t_summary} (company_location_country_region_code)",
		f"CREATE INDEX {t_summary}_stock ON {t_summary} (company_stock_symbol) WHERE company_stock_symbol IS NOT NULL",
		f"CREATE INDEX {t_summary}_start_year ON {t_summary} (company_start_year) WHERE company_start_year IS NOT NULL",
		f"CREATE INDEX {t_summary}_city_trgm ON {t_summary} USING gin (company_location_city gin_trgm_ops)",
		f"CREATE INDEX {t_summary}_domains_trgm ON {t_summary} USING gin (company_domains gin_trgm_ops)",
		f"CREATE INDEX {t_summary}_website_trgm ON {t_summary} USING gin (company_website gin_trgm_ops)",
		f"CREATE INDEX {t_summary}_legal ON {t_summary} (company_location_legal_status)",
		f"CREATE INDEX {t_summary}_domestic_hq ON {t_summary} (company_location_domestic_hq)",
	]


def create_indexes(cur, year, has_sites, only_missing=False):
	"""Summary indexes plus the raw-site index that powers the per-company sites list."""
	t_summary = f"swdb_{year}_company_summary"
	stmts = list(summary_indexes(t_summary))
	if has_sites:
		stmts.append(f"CREATE INDEX swdb_{year}_site_company_id ON swdb_{year}_site (company_id)")
	cur.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
	existing = {r[0] for r in cur.fetchall()}
	for stmt in stmts:
		name = stmt.split(" INDEX ")[1].split(" ON ")[0]
		if name in existing:
			if only_missing:
				continue
			cur.execute(f"DROP INDEX IF EXISTS {name}")
		t0 = time.time()
		try:
			cur.execute(stmt)
			log(f"INDEX {name} done in {time.time() - t0:.0f}s")
		except psycopg2.Error as exc:
			log(f"Index {name} failed ({exc.pgerror.strip() if exc.pgerror else exc}); continuing")


def add_columns(year):
	"""Backfill summary columns missing vs. COMPANY_COLUMNS / SIZING_COLUMNS, then add missing indexes."""
	t_company = f"swdb_{year}_company"
	t_sizing = f"swdb_{year}_company_tech_sizing"
	t_summary = f"swdb_{year}_company_summary"
	conn = get_db_connection()
	conn.autocommit = True
	cur = conn.cursor()
	cur.execute("SET statement_timeout = 0")
	cur.execute("SET work_mem = '2GB'")
	cur.execute("SET maintenance_work_mem = '4GB'")
	if not table_exists(cur, t_summary):
		sys.exit(f"{t_summary} does not exist; run a full build first.")

	have = existing_columns(cur, t_summary)
	for source, alias, spec in ((t_company, "c", COMPANY_COLUMNS), (t_sizing, "s", SIZING_COLUMNS)):
		if not table_exists(cur, source):
			continue
		src_cols = existing_columns(cur, source)
		missing = [(col, cast) for col, cast in spec if col in src_cols and col not in have]
		if not missing:
			continue
		log(f"Adding {', '.join(c for c, _ in missing)} from {source}")
		for col, cast in missing:
			typ = {"int": "bigint", "numeric": "numeric"}.get(cast, "text")
			cur.execute(f"ALTER TABLE {t_summary} ADD COLUMN {col} {typ}")
		sets = ", ".join(f"{col} = {cast_expr(alias, col, cast).split(' AS ')[0]}" for col, cast in missing)
		t0 = time.time()
		cur.execute(f"UPDATE {t_summary} t SET {sets} FROM {source} {alias} WHERE {alias}.company_id = t.company_id")
		log(f"Backfilled {cur.rowcount:,} rows in {(time.time() - t0) / 60:.1f} min")
		cur.execute(f"VACUUM ANALYZE {t_summary}")

	create_indexes(cur, year, table_exists(cur, f"swdb_{year}_site"), only_missing=True)
	log("Done")
	conn.close()


STATS_TABLE = "swdb_company_summary_stats"
# Keep in sync with the stats query in app.py (swdb_companies_stats_api).
STATS_SQL = """
	SELECT count(*)                                            AS companies,
		   COALESCE(sum(n_technologies), 0)                    AS tech_installs,
		   COALESCE(avg(n_technologies), 0)                    AS avg_tech,
		   percentile_cont(0.5) WITHIN GROUP (ORDER BY n_technologies) AS median_tech,
		   count(DISTINCT company_location_country)            AS countries,
		   count(DISTINCT company_primary_sic4_description)    AS industries,
		   COALESCE(sum(n_sites), 0)                           AS sites,
		   count(company_employees)                            AS with_employees,
		   percentile_cont(0.5) WITHIN GROUP (ORDER BY company_employees) AS median_employees
	FROM {table}
"""


def compute_global_stats(cur, year):
	"""Store whole-dataset aggregates for the year so the page never has to compute them live."""
	t_summary = f"swdb_{year}_company_summary"
	cur.execute(f"""
		CREATE TABLE IF NOT EXISTS {STATS_TABLE} (
			year text PRIMARY KEY, stats jsonb NOT NULL, computed_at timestamptz NOT NULL DEFAULT now()
		)""")
	log("Computing global stats…")
	t0 = time.time()
	cur.execute(STATS_SQL.format(table=t_summary))
	row = cur.fetchone()
	names = [d.name for d in cur.description]
	stats = {k: (float(v) if v is not None else None) for k, v in zip(names, row)}
	cur.execute(
		f"INSERT INTO {STATS_TABLE} (year, stats, computed_at) VALUES (%s, %s, now()) "
		f"ON CONFLICT (year) DO UPDATE SET stats = EXCLUDED.stats, computed_at = now()",
		(str(year), json.dumps(stats)),
	)
	log(f"Global stats stored in {time.time() - t0:.0f}s: {stats}")


if __name__ == "__main__":
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("year", type=int)
	ap.add_argument("--drop", action="store_true", help="drop and rebuild if the summary already exists")
	ap.add_argument("--stats-only", action="store_true", help="only refresh the stored global stats")
	ap.add_argument("--add-columns", action="store_true", help="backfill newly configured columns and missing indexes")
	args = ap.parse_args()
	if args.add_columns:
		add_columns(args.year)
	elif args.stats_only:
		conn = get_db_connection()
		conn.autocommit = True
		cur = conn.cursor()
		cur.execute("SET statement_timeout = 0")
		cur.execute("SET work_mem = '2GB'")
		compute_global_stats(cur, args.year)
		conn.close()
	else:
		build(args.year, args.drop)
