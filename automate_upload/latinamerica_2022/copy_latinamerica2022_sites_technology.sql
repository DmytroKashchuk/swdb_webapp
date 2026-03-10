-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2022/SITES_TECHNOLOGY/SITES_TECHNOLOGY.TXT

\copy latinamerica_2022_sites_technology FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2022/SITES_TECHNOLOGY/SITES_TECHNOLOGY_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
