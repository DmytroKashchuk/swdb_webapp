-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2022/SITES/SITES.TXT

\copy apac_2022_sites FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2022/SITES/SITES_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
