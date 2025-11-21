-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv4.1/SITES/SITES.txt

\copy usa_2020_rdf_sites FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/usa_2020_rdf/SITES/SITES_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER ',');
