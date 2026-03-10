-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_2020_RDFv4.1/DUNS_LooKuP/DUNS_LooKuP.TXT

\copy emea_2020_duns_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_2020_RDFv4.1/DUNS_LooKuP/DUNS_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
