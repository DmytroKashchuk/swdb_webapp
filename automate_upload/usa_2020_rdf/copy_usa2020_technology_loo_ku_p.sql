-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv4.1/TECHNOLOGY_LooKuP/TECHNOLOGY_LooKuP.TXT

\copy usa_2020_rdf_technology_lookup FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/usa_2020_rdf/TECHNOLOGY_LooKuP/TECHNOLOGY_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
