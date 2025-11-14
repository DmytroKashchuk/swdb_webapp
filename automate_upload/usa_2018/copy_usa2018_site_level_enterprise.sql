-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/SiteLevelEnterprise.TXT

\copy usa_2018_site_level_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/SiteLevelEnterprise_utf8.TXT' WITH (FORMAT csv, HEADER true);
