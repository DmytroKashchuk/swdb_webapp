-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/TechnologyTotals.TXT

\copy latinamerica_2020_technology_totals FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/TechnologyTotals_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
