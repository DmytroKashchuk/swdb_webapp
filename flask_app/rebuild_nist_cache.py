"""Rebuild the NIST categories parquet caches from the database.

Usage: python3 rebuild_nist_cache.py [australia] [usa] [all] [victims] [victims_domains] [municipalities] [municipalities_domains]
Run this after updating universe_installs_enhanced, a *_nist_controls table or
the hacked-sites source tables.
"""
import sys
import time

import app

hacked_keys = [app._hacked_cache_key(k, lv) for k in app.HACKED_DATASETS for lv in app.HACKED_LEVELS]
keys = sys.argv[1:] or list(app.NIST_COUNTRIES) + hacked_keys
for key in keys:
	t = time.time()
	if key in hacked_keys:
		ds, _, level = key.partition("_")
		df = app._hacked_build_fn(app.HACKED_DATASETS[ds], ds, level or "sites")()
	else:
		df = app._build_nist_df(app.NIST_COUNTRIES[key])
	app.NIST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	df.to_parquet(app._nist_cache_path(key), index=False)
	print(f"{key}: rebuilt in {time.time() - t:.1f}s, {len(df):,} rows", flush=True)
