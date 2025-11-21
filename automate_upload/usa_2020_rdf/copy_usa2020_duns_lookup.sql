-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2020_RDFv4.1/DUNS_LooKuP/DUNS_LooKuP.TXT

\copy usa_2020_rdf_duns_lookup FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/usa_2020_rdf/DUNS_LooKuP/DUNS_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
