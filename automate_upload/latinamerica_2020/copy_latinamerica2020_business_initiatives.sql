-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/BusinessInitiatives.TXT

\copy latinamerica_2020_business_initiatives FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/BusinessInitiatives_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
