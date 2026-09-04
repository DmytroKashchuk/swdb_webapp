"""Rebuild the NIST categories parquet caches from the database.

Usage: python3 rebuild_nist_cache.py [australia] [usa]
Run this after updating universe_installs_enhanced or a *_nist_controls table.
"""
import sys
import time

import app

countries = sys.argv[1:] or list(app.NIST_COUNTRIES)
for country in countries:
	t = time.time()
	df = app._build_nist_df(app.NIST_COUNTRIES[country])
	app.NIST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	df.to_parquet(app._nist_cache_path(country), index=False)
	print(f"{country}: rebuilt in {time.time() - t:.1f}s, {len(df):,} accounts", flush=True)
