-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv4.1/SIC_LooKuP/SIC_LooKuP.TXT

\copy usa_2020_rdf_sic_lookup FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/usa_2020_rdf/SIC_LooKuP/SIC_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
