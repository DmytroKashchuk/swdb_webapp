-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/SiteLevelEnterprise.TXT

\copy usa_2017_site_level_enterprise
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/SiteLevelEnterprise_utf8.TXT'
WITH (FORMAT csv, HEADER true);