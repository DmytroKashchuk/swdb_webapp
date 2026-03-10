-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/SiteDescription.TXT

\copy latinamerica_2020_site_description FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/SiteDescription_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
