-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2022/SITES/SITES.TXT

\copy latinamerica_2022_sites FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2022/SITES/SITES_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
