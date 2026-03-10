-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv4.1/NAICS_LooKuP/NAICS_LooKuP.TXT

\copy apac_2020_naics_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv4.1/NAICS_LooKuP/NAICS_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
