-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2021/SITES/SITES.TXT

\copy canada_2021_sites FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2021/SITES/SITES_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
