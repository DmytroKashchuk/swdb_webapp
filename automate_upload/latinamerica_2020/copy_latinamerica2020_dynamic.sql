-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/Dynamic.TXT

\copy latinamerica_2020_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/Dynamic_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
