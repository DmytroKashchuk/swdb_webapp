-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv4.1/SITES/SITES.txt

\copy apac_2020_sites FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv4.1/SITES/SITES_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER ',');
