-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2016/SiteLevelEnterprise.TXT

\copy canada_2016_site_level_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2016/SiteLevelEnterprise_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
