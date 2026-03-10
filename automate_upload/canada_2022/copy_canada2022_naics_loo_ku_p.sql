-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2022/NAICS_LooKuP/NAICS_LooKuP.TXT

\copy canada_2022_naics_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2022/NAICS_LooKuP/NAICS_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
